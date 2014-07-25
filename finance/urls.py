from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import finance.views
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', finance.views.transaction_list, name='home'),
    url(r'^list$', finance.views.transaction_list, name='list'),
    url(r'^charts/account$', finance.views.chart_account, name='chart_account'),
    url(r'^numbers/members$', finance.views.number_of_members, name='number_of_members'),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    
    url(r'^admin/import_csv', finance.views.import_csv, name='import_csv'),
    url(r'^admin/export_csv', finance.views.export_csv, name='export_csv'),
    url(r'^admin/export_members', finance.views.export_members, name='export_members'),
    url(r'^admin/backup', finance.views.backup, name='backup'),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
