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

class ProductImageCategory(orm.Model):
    """ Model name: ProductImageCategory
    """
    _name = 'product.image.category'
    _description = 'Image category'
    
    _columns = {
        'code': fields.char('Code', size=10, required=True, 
            help='Used for setup configuration parameters'),
        'name': fields.char('Name', size=64, required=True),
        'path': fields.char('Folder path', size=128, required=True,
            help='Path folder, ex.: /home/admin/photo'),
        'parent_format': fields.char('Parent format', size=60
            help='Parent code list for product composition, ex.: [3, 5]'),
        'extension_image': fields.char(
            'Extension', size=10, required=True,
            help="without dot, for ex.: jpg"
            ),
        'width': fields.integer('Max width in px.'),
        'height': fields.integer('Max height in px.'),
        'empty_image': fields.char(
            'Empty image', size=64, 
            help='Complete name + ext. of empty image, ex.: 0.jpg'),
        'upper_code': fields.boolean('Upper code',
            help='Name is code in upper case: abc10 >> ABC10.png'),
        'has_variant': fields.boolean('Has variants', 
            help='ex. for code P1010 variant 001: P1010.001.jpg'),    
        }

class ProductProductImage(osv.osv):
    ''' Add extra function and fields for manage picture for product
    '''
    _inherit = 'product.product'
     
    def _get_product_image_list(
            self, cr, uid, ids, category_id, context=None):
        ''' Return list of product and image for category_id passed
            context parameters: 
                only_name: return only name depend if file exist:
        '''        
        # Read parameters:
        context = context or {}        
        only_name = context.get('only_name', False)
        
        res = dict.fromkeys(ids, False) # init res record

        if not category_id:
            _logger.error('Category default not present in parameters!')
            return res
        
        # Read parameter for category passed:
        category_proxy = self.pool.get('product.image.category').browse(
            cr, uid, category_id, context=context)
        
        image_path = os.path.expanduser(category_proxy.path)
        #empty_image = os.path.join(image_path, category_proxy.empty_image)
        if not image_path:
            _logger.error('Path for category: %s not found!' % category_id)
            return res
        
        for product in self.browse(cr, uid, ids, context=context):            
            code = product_browse.default_code or ''
            if not code:
                _logger.error('Code not found: %s' % product.name)
                continue
            
            # Prepare code:    
            if category_proxy.upper_code:
                code = code.upper()
            else:        
                code = code.lower()
            code = code.replace(' ', '_') # no space in code
            
            # Prepare block elements:
            parent_block = [len(code)]
            try:
                if category_proxy.parent_format:
                    parent_block.extend(eval(category_proxy.parent_format))
                parent_block = parent_block.sort().reverse()
            except:
                _logger.error('Block element error: use only code')

            # Loop on block part:            
            for width in parent_block:
                parent_code = code[:width]
                image = '%s.%s' % (
                    os.path.join(image_path, parent_code),
                    category_proxy.extension_image,
                    )    
                try:
                    (filename, header) = urllib.urlretrieve(image)
                    f = open(filename , 'rb')
                    img = base64.encodestring(f.read())
                    f.close()
                except:
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
        ''' Search category for quotation picture in config and return list:
        '''
        # Search parameter: category code for quotation:
        config_pool = self.pool.get('ir.config_parameter')
        category_id = False
        config_ids = config_pool.search(cr, uid, [
            ('key', '=', 'product.image.quotation')], context=context)
         
        # Read value from code:    
        if config_ids:
            config_proxy = config_pool.browse(
                cr, uid, config_ids, context=context)[0]
            category_ids = self.pool.get('product.image.category').search(
                cr, uid, [
                    ('code', '=', config_proxy.value)], context=context)
            if category_ids:
                category_id = category_ids[0]    
        
        # Read images from folder:
        return _get_product_image_list(
            self, cr, uid, ids, category_id, context=None)    

    _columns = {
        'product_image_quotation': fields.function(
            _get_product_image_quotation, type='binary', method=True),
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
