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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
