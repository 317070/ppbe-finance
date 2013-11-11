from finance.models import Transaction
from django.shortcuts import render, render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from django.template.context import RequestContext
from finance.forms import CSVInputForm
import StringIO
import zipfile
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
import csv

def transaction_list(request):
    transaction_list = Transaction.objects.all().order_by('create_date')[:]#for debugging purposes, results should actually be paginated
    return render(request, 'transaction_list.html', {
        'transaction_list': transaction_list,
    })

@staff_member_required
def import_csv(request):
    if request.method == "POST":
        form = CSVInputForm(request.POST, request.FILES)
        success = False
        messages = ["invalid form"]
        if form.is_valid():
            (success, messages) = form.save()
        context = {"form": form, "success": success, "messages": messages}
        return render_to_response("admin/import_csv.html", context,
                                  context_instance=RequestContext(request))
    else:
        form = CSVInputForm()
        context = {"form": form}
        return render_to_response("admin/import_csv.html", context,
                                  context_instance=RequestContext(request)) 
        
@staff_member_required
def export_csv(request):
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=transactions.csv.zip'
    
    zip_file = zipfile.ZipFile( response, "w", zipfile.ZIP_DEFLATED)
    csv_file = StringIO.StringIO()
    dialect = csv.excel()
    dialect.quotechar = '"'
    dialect.delimiter = ','
    csv_writer = csv.writer(csv_file, dialect=dialect)
    
    for transaction in Transaction.objects.order_by("date"):    # generate chunk
        csv_writer.writerow([transaction.date, 
                             transaction.pirate_account.account.iban, 
                             transaction.amount, 
                             transaction.beneficiary.current_banking_account.iban,
                             transaction.BIC,
                             transaction.beneficiary.name,
                             "%s %s %s %s %s"%(transaction.beneficiary.street, transaction.beneficiary.number, transaction.beneficiary.bus, transaction.beneficiary.postal_code, transaction.beneficiary.city),
                             transaction.code,
                             transaction.statement])

    zip_file.writestr("transactions.csv",csv_file.getvalue())
    csv_file.close()
    zip_file.close()
    # generate the file
    response['Content-Length'] = response.tell()
    return response

