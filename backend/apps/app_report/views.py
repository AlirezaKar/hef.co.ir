from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_GET, require_http_methods

from apps.app_account.forms import TradingAccountForm
from apps.app_account.models import TradingAccount

from .services import (
    classify_filename,
    ensure_history_dir,
    read_history_html,
    rewrite_index_hrefs,
    rewrite_report_home_button,
    safe_resolve_history,
    scan_account_history,
)


def _file_url(filename: str) -> str:
    return reverse("report:history_file", kwargs={"filename": filename})


def _raw_url(filename: str) -> str:
    return reverse("report:history_raw", kwargs={"filename": filename})


def _home_url() -> str:
    return reverse("report:home")


def _user_owns_account(user, account: TradingAccount) -> bool:
    return account.users.filter(pk=user.pk).exists()


def _load_history_html(trading_acc_username: str, filename: str) -> str:
    path = safe_resolve_history(trading_acc_username, filename)
    if path is None:
        raise Http404("فایل تاریخچه یافت نشد")
    html = read_history_html(path)
    if classify_filename(filename, trading_acc_username) == "index":
        html = rewrite_index_hrefs(html, trading_acc_username, _file_url)
    else:
        html = rewrite_report_home_button(html, _home_url())
    return html


def _render_account_history(request, account: TradingAccount):
    acc = account.trading_acc_username
    files = scan_account_history(acc)
    if not files:
        return render(
            request,
            "report/missing.html",
            {
                "title": "فایل تاریخچه یافت نشد",
                "message": (
                    f"فایل‌های تاریخچه برای حساب «{acc}» پیدا نشد."
                ),
                "show_create": False,
                "accounts": request.user.trading_accounts.all(),
                "active_account": account,
            },
        )

    index_name = f"Index_{acc}.htm"
    path = safe_resolve_history(acc, index_name)
    if path is None:
        index_files = [f for f in files if f.report_type == "index"]
        if not index_files:
            return render(
                request,
                "report/missing.html",
                {
                    "title": "فایل تاریخچه یافت نشد",
                    "message": (
                        f"فایل فهرست تاریخچه برای حساب «{acc}» پیدا نشد."
                    ),
                    "show_create": False,
                    "accounts": request.user.trading_accounts.all(),
                    "active_account": account,
                },
            )
        index_name = index_files[0].filename

    return render(
        request,
        "report/embed.html",
        {
            "iframe_src": _raw_url(index_name),
            "filename": index_name,
            "page_title": "تاریخچه",
            "accounts": request.user.trading_accounts.all(),
            "active_account": account,
            "show_loading": True,
        },
    )


@login_required
def home_view(request):
    return render(request, "report/home.html")


@login_required
@require_GET
def history_index_view(request):
    accounts = list(request.user.trading_accounts.all())
    if not accounts:
        return render(
            request,
            "report/missing.html",
            {
                "title": "حساب ترید یافت نشد",
                "message": "حساب تریدی یافت نشد.",
                "show_create": True,
                "accounts": [],
                "active_account": None,
            },
        )

    # If only one account, open it directly; otherwise show picker.
    if len(accounts) == 1:
        return _render_account_history(request, accounts[0])

    return render(
        request,
        "report/accounts.html",
        {
            "accounts": accounts,
            "active_account": None,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def trading_account_create_view(request):
    form = TradingAccountForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        acc_username = form.cleaned_data["trading_acc_username"]
        broker = form.cleaned_data["broker"]
        existing = TradingAccount.objects.filter(
            trading_acc_username=acc_username
        ).first()

        if existing:
            existing.users.add(request.user)
            messages.success(request, "حساب ترید با موفقیت افزوده شد.")
            return redirect("report:history_account", pk=existing.pk)

        account = TradingAccount.objects.create(
            trading_acc_username=acc_username,
            broker=broker,
        )
        account.users.add(request.user)
        ensure_history_dir(acc_username)
        messages.success(request, "حساب ترید با موفقیت ایجاد شد.")
        return redirect("report:history_account", pk=account.pk)

    return render(
        request,
        "report/trading_account_form.html",
        {
            "form": form,
            "accounts": request.user.trading_accounts.all(),
        },
    )


@login_required
@require_GET
def history_account_view(request, pk: int):
    account = get_object_or_404(TradingAccount, pk=pk)
    if not _user_owns_account(request.user, account):
        raise Http404("حساب ترید یافت نشد")
    return _render_account_history(request, account)


@login_required
@require_GET
def history_file_view(request, filename: str):
    """
    Open the matching history file as a full page.
    Requires an active account ownership check via query or session-less:
    resolve against any of the user's trading accounts.
    """
    account = _resolve_account_for_file(request.user, filename)
    if account is None:
        raise Http404("فایل تاریخچه یافت نشد")
    html = _load_history_html(account.trading_acc_username, filename)
    return HttpResponse(html, content_type="text/html; charset=utf-8")


@login_required
@require_GET
@xframe_options_sameorigin
def history_raw_view(request, filename: str):
    """Serve history HTML for the index iframe embed (same-origin only)."""
    account = _resolve_account_for_file(request.user, filename)
    if account is None:
        raise Http404("فایل تاریخچه یافت نشد")
    html = _load_history_html(account.trading_acc_username, filename)
    return HttpResponse(html, content_type="text/html; charset=utf-8")


def _resolve_account_for_file(user, filename: str):
    """Find which of the user's trading accounts owns this history filename."""
    for account in user.trading_accounts.all():
        if classify_filename(filename, account.trading_acc_username):
            if safe_resolve_history(account.trading_acc_username, filename):
                return account
    return None
