import json
import io
import os
import uuid
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from .parser import parse_csv, build_dashboard_data, build_excel, KWH_PRICE_DEFAULT

UPLOAD_CACHE = os.path.join(settings.MEDIA_ROOT, "csv_cache")
os.makedirs(UPLOAD_CACHE, exist_ok=True)


def index(request):
    return render(request, "ev_app/index.html")


@require_POST
def upload(request):
    f = request.FILES.get("csv_file")
    if not f:
        return render(request, "ev_app/index.html", {"error": "No file selected."})
    if not f.name.lower().endswith(".csv"):
        return render(request, "ev_app/index.html", {"error": "Please upload a .csv file."})

    raw_bytes = f.read()
    try:
        parse_csv(io.BytesIO(raw_bytes))
    except Exception as e:
        return render(request, "ev_app/index.html", {"error": f"Could not parse file: {e}"})

    file_key   = str(uuid.uuid4()) + ".csv"
    cache_path = os.path.join(UPLOAD_CACHE, file_key)
    with open(cache_path, "wb") as out:
        out.write(raw_bytes)

    request.session["csv_key"]  = file_key
    request.session["filename"] = f.name
    return redirect("dashboard")


def _load_grp(request):
    file_key = request.session.get("csv_key")
    if not file_key:
        return None
    cache_path = os.path.join(UPLOAD_CACHE, file_key)
    if not os.path.exists(cache_path):
        return None
    with open(cache_path, "rb") as fh:
        return parse_csv(fh)


def dashboard(request):
    grp = _load_grp(request)
    if grp is None:
        return redirect("index")
    kwh_price = float(request.GET.get("price", KWH_PRICE_DEFAULT))
    data      = build_dashboard_data(grp, kwh_price)
    filename  = request.session.get("filename", "")
    return render(request, "ev_app/dashboard.html", {
        "data_json":      json.dumps(data),
        "kwh_price":      kwh_price,
        "filename":       filename,
        "months":         data["months"],
        "grand_kwh":      data["grand_kwh"],
        "grand_cost":     data["grand_cost"],
        "grand_sessions": data["grand_sessions"],
    })


def api_data(request):
    grp = _load_grp(request)
    if grp is None:
        return JsonResponse({"error": "No data loaded"}, status=400)
    kwh_price = float(request.GET.get("price", KWH_PRICE_DEFAULT))
    return JsonResponse(build_dashboard_data(grp, kwh_price))


def export_excel(request):
    grp = _load_grp(request)
    if grp is None:
        return redirect("index")
    kwh_price = float(request.GET.get("price", KWH_PRICE_DEFAULT))
    xlsx      = build_excel(grp, kwh_price)
    filename  = request.session.get("filename", "charging").replace(".csv", "")
    resp = HttpResponse(xlsx, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp["Content-Disposition"] = f'attachment; filename="{filename}_cost_report.xlsx"'
    return resp


def export_pdf(request):
    grp = _load_grp(request)
    if grp is None:
        return redirect("index")
    kwh_price = float(request.GET.get("price", KWH_PRICE_DEFAULT))
    data      = build_dashboard_data(grp, kwh_price)
    filename  = request.session.get("filename", "charging")
    html_content = render(request, "ev_app/pdf_report.html", {
        "data":      data,
        "kwh_price": kwh_price,
        "filename":  filename,
    }).content.decode("utf-8")
    from weasyprint import HTML
    pdf_bytes = HTML(string=html_content, base_url=request.build_absolute_uri("/")).write_pdf()
    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="{filename.replace(".csv","")}_cost_report.pdf"'
    return resp
