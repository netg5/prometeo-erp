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

from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.simple import redirect_to
from django.contrib.auth.decorators import permission_required
from django.template import RequestContext
from django.contrib import messages

from prometeo.core.details import ModelDetails, ModelPaginatedListDetails, value_to_string
from prometeo.core.paginator import paginate
from prometeo.core.search import search

from models import *
from forms import *
from details import *

@permission_required('partners.change_partner')
def partner_index(request):
    """Show a partner list.
    """
    search_fields, partners = search(request, Partner, exclude=['id', 'is_managed', 'is_customer', 'is_supplier', 'notes'])
        
    partners = PartnerListDetails(request, partners, exclude=['id', 'notes'])
        
    return render_to_response('partners/index.html', RequestContext(request, {'partners': partners, 'search_fields': search_fields}))

@permission_required('partners.add_partner')     
def partner_add(request):
    """Add a new partner.
    """
    if request.method == 'POST':
        form = PartnerForm(request.POST)
        if form.is_valid():
            partner = form.save()
            messages.success(request, _("Partner added"))
            return redirect_to(request, url=partner.get_absolute_url())
    else:
        form = PartnerForm()

    return render_to_response('partners/add.html', RequestContext(request, {'form': form}));

@permission_required('partners.change_partner')     
def partner_view(request, id, page=None):
    """Show partner details.
    """
    partner = get_object_or_404(Partner, pk=id)
    
    # Contacts.
    if page == 'contacts':
        contacts = ContactJobListDetails(request, partner.job_set.select_related(), exclude=['id', 'url', 'email'])
        return render_to_response('partners/contacts.html', RequestContext(request, {'partner': partner, 'contacts': contacts}))
    
    # Addresses.
    if page == 'addresses':
        addresses = PartnerAddressListDetails(partner.pk, request, partner.addresses.select_related(), exclude=['id'])
        return render_to_response('partners/addresses.html', RequestContext(request, {'partner': partner, 'addresses': addresses}))
    
    # Telephones.
    if page == 'telephones':
        telephones = PartnerTelephoneListDetails(partner.pk, request, partner.telephones.select_related(), exclude=['id'])
        return render_to_response('partners/telephones.html', RequestContext(request, {'partner': partner, 'telephones': telephones}))
    
    # Details.
    details = PartnerDetails(instance=partner)
    return render_to_response('partners/view.html', RequestContext(request, {'partner': partner, 'details': details}))

@permission_required('partners.change_partner')     
def partner_edit(request, id):
    """Edit a partner.
    """
    partner = get_object_or_404(Partner, pk=id)
    if request.method == 'POST':
        form = PartnerForm(request.POST, instance=partner)
        if form.is_valid():
            form.save()
            messages.success(request, _("Partner updated"))
            return redirect_to(request, url=partner.get_absolute_url())
    else:
        form = PartnerForm(instance=partner)
    return render_to_response('partners/edit.html', RequestContext(request, {'partner': partner, 'form': form}))

@permission_required('partners.delete_partner')    
def partner_delete(request, id):
    """Delete a partner.
    """
    partner = get_object_or_404(Partner, pk=id)
    if request.method == 'POST':
        if (request.POST.has_key(u'yes')):
            partner.delete()
            messages.success(request, _("Partner deleted"))
            return redirect_to(request, url='/partners/');
        return redirect_to(request, url=partner.get_absolute_url())
    return render_to_response('partners/delete.html', RequestContext(request, {'partner': partner}))
    
@permission_required('partners.change_partner')
def partner_suppliers(request):
    """Show a supplier list.
    """
    search_fields, partners = search(request, Partner, exclude=['id', 'is_managed', 'is_customer', 'is_supplier', 'notes'])
        
    partners = PartnerListDetails(request, partners.filter(is_supplier=True), exclude=['id', 'is_customer', 'is_supplier', 'notes'])
        
    return render_to_response('partners/suppliers.html', RequestContext(request, {'partners': partners, 'search_fields': search_fields}))
    
@permission_required('partners.change_partner')
def partner_customers(request):
    """Show a customer list.
    """
    search_fields, partners = search(request, Partner, exclude=['id', 'is_managed', 'is_customer', 'is_supplier', 'notes'])
        
    partners = PartnerListDetails(request, partners.filter(is_customer=True), exclude=['id', 'is_customer', 'is_supplier', 'notes'])
        
    return render_to_response('partners/customers.html', RequestContext(request, {'partners': partners, 'search_fields': search_fields}))
    
@permission_required('partners.change_partner')
def partner_add_telephone(request, id):
    """Add a new telephone number for the partner.
    """
    partner = get_object_or_404(Partner, pk=id)
    
    if request.method == 'POST':
        form = TelephoneForm(request.POST)
        if form.is_valid():
            telephone = form.save()
            partner.telephones.add(telephone)
            messages.success(request, _("Telephone number added"))
            return redirect_to(request, url=partner.get_telephones_url())
    else:
        form = TelephoneForm()

    return render_to_response('partners/add_telephone.html', RequestContext(request, {'partner': partner, 'form': form}));
    
@permission_required('partners.change_partner')
def partner_edit_telephone(request, id, telephone_id):
    """Edit a telephone number of the partner.
    """
    partner = get_object_or_404(Partner, pk=id)
    telephone = get_object_or_404(Telephone, pk=telephone_id)
    if telephone.partner_set.get(id=partner.pk) is None:
        raise Http404
    
    if request.method == 'POST':
        form = TelephoneForm(request.POST, instance=telephone)
        if form.is_valid():
            form.save()
            messages.success(request, _("Telephone number updated"))
            return redirect_to(request, url=partner.get_telephones_url())
    else:
        form = TelephoneForm(instance=telephone)

    return render_to_response('partners/edit_telephone.html', RequestContext(request, {'partner': partner, 'telephone': telephone, 'form': form}));
    
@permission_required('partners.change_partner')    
def partner_delete_telephone(request, id, telephone_id):
    """Delete a partner's telephone number.
    """
    partner = get_object_or_404(Partner, pk=id)
    telephone = get_object_or_404(Telephone, pk=telephone_id)
    if telephone.partner_set.get(id=partner.pk) is None:
        raise Http404

    if request.method == 'POST':
        if (request.POST.has_key(u'yes')):
            telephone.delete()
            messages.success(request, _("Telephone number deleted"))
        return redirect_to(request, url=partner.get_telephones_url())
    return render_to_response('partners/delete_telephone.html', RequestContext(request, {'partner': partner, 'telephone': telephone})) 
    
@permission_required('partners.change_partner')
def partner_add_address(request, id):
    """Add a new address for the partner.
    """
    partner = get_object_or_404(Partner, pk=id)
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save()
            partner.addresses.add(address)
            messages.success(request, _("Address added"))
            return redirect_to(request, url=partner.get_addresses_url())
    else:
        form = AddressForm()

    return render_to_response('partners/add_address.html', RequestContext(request, {'partner': partner, 'form': form}));
    
@permission_required('partners.change_partner')
def partner_edit_address(request, id, address_id):
    """Edit a address of the partner.
    """
    partner = get_object_or_404(Partner, pk=id)
    address = get_object_or_404(Address, pk=address_id)
    if address.partner_set.get(id=partner.pk) is None:
        raise Http404
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, _("Address updated"))
            return redirect_to(request, url=partner.get_addresses_url())
    else:
        form = AddressForm(instance=address)

    return render_to_response('partners/edit_address.html', RequestContext(request, {'partner': partner, 'address': address, 'form': form}));
    
@permission_required('partners.change_partner')    
def partner_delete_address(request, id, address_id):
    """Delete a partner's address.
    """
    partner = get_object_or_404(Partner, pk=id)
    address = get_object_or_404(Address, pk=address_id)
    if address.partner_set.get(id=partner.pk) is None:
        raise Http404

    if request.method == 'POST':
        if (request.POST.has_key(u'yes')):
            address.delete()
            messages.success(request, _("Address deleted"))
        return redirect_to(request, url=partner.get_addresses_url())
    return render_to_response('partners/delete_address.html', RequestContext(request, {'partner': partner, 'address': address})) 
    
@permission_required('partners.change_partner')
def partner_add_contact(request, id):
    """Add a new contact for the partner.
    """
    partner = get_object_or_404(Partner, pk=id)
    job = Job(partner=partner)
    
    if request.method == 'POST':
        form = PartnerJobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, _("Contact added"))
            return redirect_to(request, url=partner.get_contacts_url())
    else:
        form = PartnerJobForm(instance=job)

    return render_to_response('partners/add_contact.html', RequestContext(request, {'partner': partner, 'form': form}));
    
@permission_required('partners.change_partner')
def partner_edit_contact(request, id, job_id):
    """Edit a contact of the partner.
    """
    partner = get_object_or_404(Partner, pk=id)
    job = get_object_or_404(Job, pk=job_id)
    if job.partner != partner:
        raise Http404
    
    if request.method == 'POST':
        form = PartnerJobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, _("Contact updated"))
            return redirect_to(request, url=partner.get_contacts_url())
    else:
        form = PartnerJobForm(instance=job)

    return render_to_response('partners/edit_contact.html', RequestContext(request, {'partner': partner, 'job': job, 'form': form}));
    
@permission_required('partners.change_partner')    
def partner_delete_contact(request, id, job_id):
    """Delete a partner's contact.
    """
    partner = get_object_or_404(Partner, pk=id)
    job = get_object_or_404(Job, pk=job_id)
    if job.partner != partner:
        raise Http404

    if request.method == 'POST':
        if (request.POST.has_key(u'yes')):
            job.delete()
            messages.success(request, _("Contact removed"))
        return redirect_to(request, url=partner.get_contacts_url())
    return render_to_response('partners/delete_contact.html', RequestContext(request, {'partner': partner, 'job': job}))

@permission_required('partners.change_contact')
def contact_index(request):
    """Show a contact list.
    """
    search_fields, contacts = search(request, Contact, exclude=['id', 'notes'])
        
    contacts = ModelPaginatedListDetails(request, contacts, exclude=['id', 'notes'])
        
    return render_to_response('partners/contacts/index.html', RequestContext(request, {'contacts': contacts, 'search_fields': search_fields}))

@permission_required('partners.add_contact')     
def contact_add(request):
    """Add a new contact.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, _("Contact added"))
            return redirect_to(request, url=contact.get_absolute_url())
    else:
        form = ContactForm()

    return render_to_response('partners/contacts/add.html', RequestContext(request, {'form': form}));

@permission_required('partners.change_contact')     
def contact_view(request, id, page=None):
    """Show contact details.
    """
    contact = get_object_or_404(Contact, pk=id)
    
    # Jobs.
    if page == 'jobs':
        jobs = PartnerJobListDetails(request, contact.job_set.select_related())
        return render_to_response('partners/contacts/jobs.html', RequestContext(request, {'contact': contact, 'jobs': jobs}))
    
    # Addresses.
    if page == 'addresses':
        addresses = ContactAddressListDetails(contact.pk, request, contact.addresses.select_related(), exclude=['id'])
        return render_to_response('partners/contacts/addresses.html', RequestContext(request, {'contact': contact, 'addresses': addresses}))
    
    # Telephones.
    if page == 'telephones':
        telephones = ContactTelephoneListDetails(contact.pk, request, contact.telephones.select_related(), exclude=['id'])
        return render_to_response('partners/contacts/telephones.html', RequestContext(request, {'contact': contact, 'telephones': telephones}))
    
    # Details.
    details = ContactDetails(instance=contact)
    return render_to_response('partners/contacts/view.html', RequestContext(request, {'contact': contact, 'details': details}))

@permission_required('partners.change_contact')     
def contact_edit(request, id):
    """Edit a contact.
    """
    contact = get_object_or_404(Contact, pk=id)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, _("Contact updated"))
            return redirect_to(request, url=contact.get_absolute_url())
    else:
        form = ContactForm(instance=contact)
    return render_to_response('partners/contacts/edit.html', RequestContext(request, {'contact': contact, 'form': form}))

@permission_required('partners.delete_contact')    
def contact_delete(request, id):
    """Delete a contact.
    """
    contact = get_object_or_404(Contact, pk=id)
    if request.method == 'POST':
        if (request.POST.has_key(u'yes')):
            contact.delete()
            messages.success(request, _("Contact deleted"))
            return redirect_to(request, url='/partners/contacts/');
        return redirect_to(request, url=contact.get_absolute_url())
    return render_to_response('partners/contacts/delete.html', RequestContext(request, {'contact': contact}))
    
@permission_required('partners.change_contact')
def contact_add_telephone(request, id):
    """Add a new telephone number for the contact.
    """
    contact = get_object_or_404(Contact, pk=id)
    
    if request.method == 'POST':
        form = TelephoneForm(request.POST)
        if form.is_valid():
            telephone = form.save()
            contact.telephones.add(telephone)
            messages.success(request, _("Telephone number added"))
            return redirect_to(request, url=contact.get_telephones_url())
    else:
        form = TelephoneForm()

    return render_to_response('partners/contacts/add_telephone.html', RequestContext(request, {'contact': contact, 'form': form}));
    
@permission_required('partners.change_contact')
def contact_edit_telephone(request, id, telephone_id):
    """Edit a telephone number of the contact.
    """
    contact = get_object_or_404(Contact, pk=id)
    telephone = get_object_or_404(Telephone, pk=telephone_id)
    if telephone.contact_set.get(id=contact.pk) is None:
        raise Http404
    
    if request.method == 'POST':
        form = TelephoneForm(request.POST, instance=telephone)
        if form.is_valid():
            form.save()
            messages.success(request, _("Telephone number updated"))
            return redirect_to(request, url=contact.get_telephones_url())
    else:
        form = TelephoneForm(instance=telephone)

    return render_to_response('partners/contacts/edit_telephone.html', RequestContext(request, {'contact': contact, 'telephone': telephone, 'form': form}));
    
@permission_required('partners.change_contact')    
def contact_delete_telephone(request, id, telephone_id):
    """Delete a contact's telephone number.
    """
    contact = get_object_or_404(Contact, pk=id)
    telephone = get_object_or_404(Telephone, pk=telephone_id)
    if telephone.contact_set.get(id=contact.pk) is None:
        raise Http404

    if request.method == 'POST':
        if (request.POST.has_key(u'yes')):
            telephone.delete()
            messages.success(request, _("Telephone number deleted"))
        return redirect_to(request, url=contact.get_telephones_url())
    return render_to_response('partners/contacts/delete_telephone.html', RequestContext(request, {'contact': contact, 'telephone': telephone})) 
    
@permission_required('partners.change_contact')
def contact_add_address(request, id):
    """Add a new address for the contact.
    """
    contact = get_object_or_404(Contact, pk=id)
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save()
            contact.addresses.add(address)
            messages.success(request, _("Address added"))
            return redirect_to(request, url=contact.get_addresses_url())
    else:
        form = AddressForm()

    return render_to_response('partners/contacts/add_address.html', RequestContext(request, {'contact': contact, 'form': form}));
    
@permission_required('partners.change_contact')
def contact_edit_address(request, id, address_id):
    """Edit a address of the contact.
    """
    contact = get_object_or_404(Contact, pk=id)
    address = get_object_or_404(Address, pk=address_id)
    if address.contact_set.get(id=contact.pk) is None:
        raise Http404
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, _("Address updated"))
            return redirect_to(request, url=contact.get_addresses_url())
    else:
        form = AddressForm(instance=address)

    return render_to_response('partners/contacts/edit_address.html', RequestContext(request, {'contact': contact, 'address': address, 'form': form}));
    
@permission_required('partners.change_contact')    
def contact_delete_address(request, id, address_id):
    """Delete a contact's address.
    """
    contact = get_object_or_404(Contact, pk=id)
    address = get_object_or_404(Address, pk=address_id)
    if address.contact_set.get(id=contact.pk) is None:
        raise Http404

    if request.method == 'POST':
        if (request.POST.has_key(u'yes')):
            address.delete()
            messages.success(request, _("Address deleted"))
        return redirect_to(request, url=contact.get_addresses_url())
    return render_to_response('partners/contacts/delete_address.html', RequestContext(request, {'contact': contact, 'address': address})) 
    
@permission_required('partners.change_contact')
def contact_add_job(request, id):
    """Add a new job for the contact.
    """
    contact = get_object_or_404(Contact, pk=id)
    job = Job(contact=contact)
    
    if request.method == 'POST':
        form = ContactJobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, _("Job added"))
            return redirect_to(request, url=contact.get_jobs_url())
    else:
        form = ContactJobForm(instance=job)

    return render_to_response('partners/contacts/add_job.html', RequestContext(request, {'contact': contact, 'form': form}));
    
@permission_required('partners.change_contact')
def contact_edit_job(request, id, job_id):
    """Edit a job of the contact.
    """
    contact = get_object_or_404(Contact, pk=id)
    job = get_object_or_404(Job, pk=job_id)
    if job.contact != contact:
        raise Http404
    
    if request.method == 'POST':
        form = ContactJobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, _("Job updated"))
            return redirect_to(request, url=contact.get_jobs_url())
    else:
        form = ContactJobForm(instance=job)

    return render_to_response('partners/contacts/edit_job.html', RequestContext(request, {'contact': contact, 'job': job, 'form': form}));
    
@permission_required('partners.change_contact')    
def contact_delete_job(request, id, job_id):
    """Delete a contact's job.
    """
    contact = get_object_or_404(Contact, pk=id)
    job = get_object_or_404(Job, pk=job_id)
    if job.contact != contact:
        raise Http404

    if request.method == 'POST':
        if (request.POST.has_key(u'yes')):
            job.delete()
            messages.success(request, _("Job deleted"))
        return redirect_to(request, url=contact.get_jobs_url())
    return render_to_response('partners/contacts/delete_job.html', RequestContext(request, {'contact': contact, 'job': job}))
    
@permission_required('partners.change_role')
def role_index(request):
    """Show a role list.
    """
    search_fields, roles = search(request, Role)
        
    roles = ModelPaginatedListDetails(request, roles)
        
    return render_to_response('partners/contacts/roles/index.html', RequestContext(request, {'roles': roles, 'search_fields': search_fields}))

@permission_required('partners.add_role')     
def role_add(request):
    """Add a new role.
    """
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            messages.success(request, _("Role added"))
            return redirect_to(request, url=role.get_absolute_url())
    else:
        form = RoleForm()

    return render_to_response('partners/contacts/roles/add.html', RequestContext(request, {'form': form}));

@permission_required('partners.change_role')     
def role_view(request, id, page=None):
    """Show role details.
    """
    role = get_object_or_404(Role, pk=id)
    details = ModelDetails(instance=role)
    return render_to_response('partners/contacts/roles/view.html', RequestContext(request, {'role': role, 'details': details}))

@permission_required('partners.change_role')     
def role_edit(request, id):
    """Edit a role.
    """
    role = get_object_or_404(Role, pk=id)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, _("Role updated"))
            return redirect_to(request, url=role.get_absolute_url())
    else:
        form = RoleForm(instance=role)
    return render_to_response('partners/contacts/roles/edit.html', RequestContext(request, {'role': role, 'form': form}))

@permission_required('partners.delete_role')    
def role_delete(request, id):
    """Delete a role.
    """
    role = get_object_or_404(Role, pk=id)
    if request.method == 'POST':
        if (request.POST.has_key(u'yes')):
            role.delete()
            messages.success(request, _("Role deleted"))
            return redirect_to(request, url='/partners/contacts/roles/');
        return redirect_to(request, url=role.get_absolute_url())
    return render_to_response('partners/contacts/roles/delete.html', RequestContext(request, {'role': role}))
