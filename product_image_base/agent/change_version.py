#!/usr/bin/python
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

ren_list = []
log_f = open('log_file.csv', 'w')
for root, folders, files in os.walk('.'):
    for file_o in files:
        if file_o[-8:-5] == '-00' and file_o[-4:] == '.jpg':
            file_d = '%s.%s' % (
                file_o[:-8],
                file_o[-7:],
                
                )
            full_o = os.path.join(root, file_o)
            full_d = os.path.join(root, file_d)
            log_f.write('%s | %s\n' % (
                file_o,
                file_d,
                ))
            ren_list.append((full_o, full_d))
        else:    
            log_f.write('%s | JUMPED\n' % file_o)
            
for full_o, full_d in ren_list:
    os.rename(full_o, full_d)
             
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
