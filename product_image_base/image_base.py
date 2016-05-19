# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2001-2014 Micronaet SRL (<http://www.micronaet.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import os
import sys
import logging
import openerp
import urllib
import base64
import openerp.netsvc as netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class ProductImageAlbum(orm.Model):
    """ Model name: ProductImageAlbum
    """
    _name = 'product.image.album'
    _description = 'Image album'
    
    _columns = {
        'code': fields.char('Code', size=10, required=True, 
            help='Used for setup configuration parameters'),
        'name': fields.char('Name', size=64, required=True),
        'path': fields.char('Folder path', size=128, required=True,
            help='Path folder, ex.: /home/admin/photo'),
        'parent_format': fields.char('Parent format', size=60,
            help='Parent code list for product composition, ex.: 3|5'),
        'extension_image': fields.char(
            'Extension', size=10, required=True,
            help="Without dot, for ex.: jpg"
            ),
        'max_width': fields.integer('Max width in px.'),
        'max_height': fields.integer('Max height in px.'),
        'empty_image': fields.char(
            'Empty image', size=64, 
            help='Complete name + ext. of empty image, ex.: 0.jpg'),
        'upper_code': fields.boolean('Upper code',
            help='Name is code in upper case: abc10 >> ABC10.png'),
        'has_variant': fields.boolean('Has variants', 
            help='ex. for code P1010 variant 001: P1010-001.jpg'),
        }

class ProductImageFile(orm.Model):
    """ Model name: ProductImageFile
    """
    _name = 'product.image.file'
    _description = 'Image file'
    _rec_name = 'filename'
    _order = 'filename'

    # -----------------
    # Utility function:
    # -----------------
    def get_default_code(self, variant, filename):
        ''' Function that extract default_code from filename)
        '''
        # TODO test upper and test extension
        block = filename.split('.')
        if len(block) == 2:
            return (
                block[0].replace('_', ' '),
                False,
                block[1]
                )
        if len(block) == 3: # variant 
            return (
                block[0].replace('_', ' '),
                block[1],                
                block[2],
                )
        else:        
            return (
                block[0].replace('_', ' '),
                False,
                '', # no extension when error
                )
            
        
    def load_syncro_image_album(self, cr, uid, album_ids, context=None):
        ''' Import image folder for proxy  
        '''
        # Pool used:
        album_pool = self.pool.get('product.image.album')
        product_pool = self.pool.get('product.product')

        exist_ids = [] # for all albums        
        for album in album_pool.browse(cr, uid, album_ids, context=context):
            # Parameters:
            path = os.path.expanduser(album.path)        
            extension_image = album.extension_image
            # TODO manage upper case or lower case and variant!
            upper_code = album.upper_code
            has_variant = album.has_variant

            # Load file current loaded in album folder:
            old_filenames = {}
            for old_file in album.image_ids:
                old_filenames[old_file.filename] = (
                    old_file.id, old_file.timestamp)
            
            # Read all files in folder:
            for root, directories, files in os.walk(path):
                for filename in files:
                    fullname = os.path.join(root, filename)                
                    timestamp = '%s' % os.path.getmtime(fullname)
                    default_code, variant, extension = self.get_default_code(
                        filename)
                        
                    product_ids = product_pool.search(cr, uid, [
                        ('default_code', '=', default_code)], context=context)
                    if product_ids:
                        if len(product_ids) > 1:
                            _logger.error('More than one product code: %s' % (
                                default_code))
                        product_id = product_ids[0]            
                    else:
                        product_id = False    
                    
                    data = {
                        'filename': filename,
                        'album_id': album.id,
                        'timestamp': timestamp,
                        'product_id': product_id, 
                        'extension': extension,
                        # Used?:
                        #'width': fields.integer('Width px.'),
                        #'height': fields.integer('Height px.'),
                        }
                    if variant:
                        data['variant'] = True
                        data_code['variant'] = variant                            
                        
                    # Status error case:    
                    if extension != extension_image:
                        data['status'] = 'format'
                    elif not product_id:
                        data['status'] = 'product'
                    
                    if filename in old_filenames:                  
                        # Check timestamp for update
                        item_id = old_filenames[filename][0]
                        # Check also status error not present:
                        if 'status' not in data and \
                                timestamp != old_filenames[filename][1]:
                            data['status'] = 'modify'                            
                           
                        self.write(cr, uid, item_id, data, context=context)                            
                            
                    else: # Create (default modify)
                        item_id = self.create(
                            cr, uid, data, context=context)
                    if item_id:        
                        exist_ids.append(item_id) # after will force exist
        
        # Mark image no more present (for all albums):
        not_exist_ids = self.search(cr, uid, [
            ('id', 'not in', exist_ids)], context=context)            
        return self.write(cr, uid, not_exist_ids, {
            'status': 'removed'}, context=context)    
    
    # -----------------
    # Scheduled action:
    # -----------------
    def syncro_image_album(self, cr, uid, context=None):
        ''' Import image for album marked (not calculated)
        '''
        # pool used:
        album_pool = self.pool.get('product.image.album')

        # ---------------------------------------        
        # Load all image in album not calculated:
        # ---------------------------------------       
        album_ids = album_pool.search(cr, uid, [
            ('calculated', '=', False)], context=context)        
        self.load_syncro_image_album(cr, uid, album_ids, context=context)

        # TODO Calculate image
        
        # TODO Load all image in album and reload elements:
                
        return True
    
    _columns = {
        'filename': fields.char('Filename', size=60, required=True),
        'album_id': fields.many2one('product.image.album', 'album'), 
        'timestamp': fields.char('Timestamp', size=30),
        'variant': fields.boolean('Variant', 
            help='File format CODE-XXX.jpg where XXX is variant block'),
        'variant_code': fields.char('Variant code', size=5),
        'product_id': fields.many2one('product.product', 'Product'),

        # Used?:
        'width': fields.integer('Width px.'),
        'height': fields.integer('Height px.'),
        'extension': fields.char(
            'Extension', size=10, help='Without dot, for ex.: jpg'),
        'status': fields.selection([
            ('ok', 'OK'),
            ('modify', 'File modify'),
            ('removed', 'File removed'),
            ('format', 'Wrong format'),
            ('product', 'No product'),
            ], 'status'),
        # TODO file image binary         
        }
        
    _defaults = {
        'status': lambda *x: 'modify',
        }    

class ProductImageAlbumCalculated(orm.Model):
    """ Add fields for manage calculated folders
    """
    _inherit = 'product.image.album'

    _columns = {        
        # -------------------
        # Redimension fields:
        # -------------------
        'calculated': fields.boolean('Calculated', 
            help='Folder is calculated from another images'),
        'album_id': fields.many2one(
            'product.image.album', 'Parent album', 
            domain=[('calculated', '=', False)]),
         
        # Dimension for calculating:    
        'width': fields.integer('Width in px.'),
        'height': fields.integer('Height in px.'),
        'redimension_type' :fields.selection([
            ('length', 'Max length'),
            ('width', 'Max width'),
            ('max', 'Max large (lenght or width)'),            
            ], 'Redimension type'),

        # ----------------------
        # Relation 2many fields:
        # ----------------------
        'image_ids': fields.one2many(
            'product.image.file', 'album_id', 'Files'),
        }

    _defaults = {
        # Default value:
        'redimension_type:': lambda *x: 'max',    
        }

class ProductProductImage(osv.osv):
    ''' Add extra function and fields for manage picture for product
    '''
    _inherit = 'product.product'
     
    def _get_product_image_list(
            self, cr, uid, ids, album_id, context=None):
        ''' Return list of product and image for album_id passed
            context parameters: 
                only_name: return only name depend if file exist:
        '''  
        # Read parameters:
        context = context or {}        
        only_name = context.get('only_name', False)
        
        res = dict.fromkeys(ids, False) # init res record

        if not album_id:
            _logger.error('album default not present in parameters!')
            return res
        
        # Read parameter for album passed:
        album_proxy = self.pool.get('product.image.album').browse(
            cr, uid, album_id, context=context)

        image_path = os.path.expanduser(album_proxy.path)
        #empty_image = os.path.join(image_path, album_proxy.empty_image)
        if not image_path:
            _logger.error('Path for album: %s not found!' % album_id)
            return res
        for product in self.browse(cr, uid, ids, context=context):            
            code = product.default_code or ''
            if not code:
                _logger.error('Code not found: %s' % product.name)
                continue

            # Prepare code:    
            if album_proxy.upper_code:
                code = code.upper()
            else:        
                code = code.lower()
            code = code.replace(' ', '_') # no space in code
            
            # Prepare block elements:
            parent_block = [len(code)]
            try:
                if album_proxy.parent_format:
                    for item in album_proxy.parent_format.split('|'):
                        parent_block.append(int(item))
                parent_block.sort()
                parent_block.reverse()
            except:
                _logger.error('Block element error: use only code')

            # Loop on block part:            
            for width in parent_block:
                parent_code = code[:width]
                image = '%s.%s' % (
                    os.path.join(image_path, parent_code),
                    album_proxy.extension_image,
                    )    
                try:
                    (filename, header) = urllib.urlretrieve(image)
                    f = open(filename , 'rb')
                    img = base64.encodestring(f.read())
                    f.close()
                except:
                    _logger.warning('Image not found: %s' % image)
                    img = False
                if img:
                    if only_name:
                        res[product.id] = image
                    else:
                        res[product.id] = img
                    break # no more elements (found first)
        return res

    def _get_product_image_quotation(self, cr, uid, ids, field_name, arg, 
            context=None):
        ''' Search album for quotation picture in config and return list:
            context parameters:
                'product_image': image code to open, ex.: QUOTATION (default)
        '''
        context = context or {}
        # TODO add test for load image or not depend on user setting or report
            
        # ----------------------
        # A. Passed code for image:
        # ----------------------
        product_image = context.get('product_image', False)
        
        if not product_image:
            # --------------------
            # B. Config parameter:
            # --------------------
            config_pool = self.pool.get('ir.config_parameter')
            config_ids = config_pool.search(cr, uid, [
                ('key', '=', 'product.image.quotation')], context=context)
         
            # Read value from code:    
            if config_ids:
                config_proxy = config_pool.browse(
                    cr, uid, config_ids, context=context)[0]
                product_image = config_proxy.value                

        # -------------------------------
        # Try to read album if present
        # (passed or config parameter)
        # -------------------------------        
        album_ids = self.pool.get('product.image.album').search(
            cr, uid, [('code', '=', product_image)], context=context)
        if album_ids:
            album_id = album_ids[0]    
        else:    
            album_id = False
        
        # Read images from folder:
        return self._get_product_image_list(
            cr, uid, ids, album_id, context=None)    

    _columns = {
        'product_image_quotation': fields.function(
            _get_product_image_quotation, type='binary', method=True),
        }        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
