from django.shortcuts import redirect
from finance.models import Transaction, Person
from django.shortcuts import render, render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from django.template.context import RequestContext
from finance.forms import CSVInputForm
import StringIO
import zipfile
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
import csv
from datetime import datetime
import os

def transaction_list(request):
    transaction_list = Transaction.objects.filter(public=True).order_by('date')[::-1]#for debugging purposes, results should actually be paginated
    return render(request, 'transaction_list.html', {
        'transaction_list': transaction_list,
    })

def chart_account(request):
    transactions = Transaction.objects.filter(public=True).order_by('date')[:]
    
    data = []
    account = 0.0
    for transaction in transactions:
        account += transaction.amount
        date = "Date.UTC(%d,%d,%d)"%(transaction.date.year,transaction.date.month-1,transaction.date.day)
        data.append([date, account])
    money_data = str(data)
    money_data = money_data.replace("'", "")
    money_data = money_data.replace("\"", "")
    
    return render(request, 'chart_account.html', {
        'money_data': money_data,
    })


@staff_member_required
def backup(request):
    PRIVATE_ROOT = "/home/jonas/git/ppbe-finance/"
    newfile = 'sqlite.db.back.{:%Y.%m.%d}'.format(datetime.now())
    if os.path.isfile(PRIVATE_ROOT + newfile):
        index = 1
        while os.path.isfile( PRIVATE_ROOT + "%s.%d" % (newfile,index) ):
            index += 1
        newfile = "%s.%d" % (newfile,index)
    os.system('cp ' + PRIVATE_ROOT + "sqlite.db" + ' ' + \
        PRIVATE_ROOT + newfile)
    return redirect('/admin/')   

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
                             transaction.beneficiary.current_banking_account.iban if transaction.beneficiary.current_banking_account else "",
                             transaction.BIC,
                             transaction.beneficiary.lastname+" "+transaction.beneficiary.firstname,
                             "%s %s %s"%(transaction.beneficiary.street, transaction.beneficiary.postal_code, transaction.beneficiary.city),
                             transaction.code,
                             transaction.statement.encode("utf-8")])

    zip_file.writestr("transactions.csv",csv_file.getvalue())
    csv_file.close()
    zip_file.close()
    # generate the file
    response['Content-Length'] = response.tell()
    return response

@staff_member_required
def export_members(request):
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=transactions.csv.zip'
    
    zip_file = zipfile.ZipFile( response, "w", zipfile.ZIP_DEFLATED)
    csv_file = StringIO.StringIO()
    dialect = csv.excel()
    dialect.quotechar = '"'
    dialect.delimiter = ','
    csv_writer = csv.writer(csv_file, dialect=dialect)
    
    for person in Person.objects.order_by("postal_code"):    # generate chunk
        csv_writer.writerow([person.firstname.encode("utf-8"),
                             person.lastname.encode("utf-8"),
                             person.email_address,
                             person.street.encode("utf-8"),
                             person.postal_code,
                             person.city.encode("utf-8"),
                             person.telephone,
                             person.language,
                             person.notas.encode("utf-8"),
                             person.last_payment_date])

    zip_file.writestr("transactions.csv",csv_file.getvalue())
    csv_file.close()
    zip_file.close()
    # generate the file
    response['Content-Length'] = response.tell()
    return response


