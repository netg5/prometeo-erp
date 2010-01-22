#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This file is part of the prometeo project.

This program is free software: you can redistribute it and/or modify it 
under the terms of the GNU Lesser General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

__author__ = 'Emanuele Bertoldi <zuck@fastwebnet.it>'
__copyright__ = 'Copyright (c) 2010 Emanuele Bertoldi'
__version__ = '$Revision$'

from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.simple import redirect_to
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.db.models import Q

from prometeo.core.details import ModelDetails

from models import Warehouse
from forms import WarehouseForm

@login_required 
def index(request):
    """Show a warehouse list.
    """
    warehouses = None
    queryset = None

    if request.method == 'POST' and request.POST.has_key(u'search'):
        token = request.POST['query']
        queryset = Q(name__startswith=token) | Q(name__endswith=token)

    if (queryset is not None):
        warehouses = Warehouse.objects.filter(queryset)
    else:
        warehouses = Warehouse.objects.all()
        
    return render_to_response('warehouses/index.html', RequestContext(request, {'warehouses': warehouses}))
 
@login_required    
def add(request):
    """Add a new warehouse.
    """
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            warehouse = form.save()
            return redirect_to(request, url='/warehouses/view/%s/' % (warehouse.pk))
    else:
        form = WarehouseForm()

    return render_to_response('warehouses/add.html', RequestContext(request, {'form': form}));

@login_required     
def view(request, id):
    """Show warehouse details.
    """
    warehouse = get_object_or_404(Warehouse, pk=id)
    details = ModelDetails(instance=warehouse)
    return render_to_response('warehouses/view.html', RequestContext(request, {'warehouse': warehouse, 'details': details}))

@login_required     
def edit(request, id):
    """Edit a warehouse.
    """
    warehouse = Warehouse.objects.get(pk=id)
    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            return redirect_to(request, url='/warehouses/view/%s/' % (id))
    else:
        form = WarehouseForm(instance=warehouse)
    return render_to_response('warehouses/edit.html', RequestContext(request, {'warehouse': warehouse, 'form': form}))

@login_required    
def delete(request, id):
    """Delete a warehouse.
    """
    warehouse = get_object_or_404(Warehouse, pk=id)
    if request.method == 'POST':
        if (request.POST.has_key(u'yes')):
            warehouse.delete()
            return redirect_to(request, url='/warehouses/');
        return redirect_to(request, url='/warehouses/view/%s/' % (id))
    return render_to_response('warehouses/delete.html', RequestContext(request, {'warehouse': warehouse}))