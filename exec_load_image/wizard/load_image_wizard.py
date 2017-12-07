# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


import os
import sys
import logging
import openerp
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)


class IrCronForceImageWizard(orm.TransientModel):
    ''' Wizard for force schedule action load image
    '''
    _name = 'ir.cron.force.image.wizard'

    # --------------------
    # Wizard button event:
    # --------------------
    def action_force(self, cr, uid, ids, context=None):
        ''' Event for button done
        '''
        if context is None: 
            context = {}        


        cron_pool = self.pool.get('ir.cron')
        cron_ids = cron_pool.search(cr, uid, [
            ('function', 'ilike', 'syncro_image_album'),
            ('model', '=', 'product.image.file'),
            ], context=context)
            
        if cron_ids:
            cron_ids = [cron_ids[0], ] # only first
            return cron_pool.exec_manually(cr, uid, cron_ids, context=context)
        else:
            raise osv.except_osv(
                _('Errore'), 
                _('Non trovo la schedulazione per syncro_image_album'),
                )    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
