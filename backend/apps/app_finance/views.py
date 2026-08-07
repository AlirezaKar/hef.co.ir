from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods

from apps.app_account.forms import TradingAccountForm
from apps.app_account.models import TradingAccount

from .services import (
    classify_filename,
    ensure_history_dir,
    ensure_index_home_button,
    read_history_html,
    rewrite_home_button,
    rewrite_index_hrefs,
    safe_resolve_history,
    scan_account_history,
)


def _file_url(filename: str) -> str:
    return reverse("finance:history_file", kwargs={"filename": filename})


def _home_url() -> str:
    return reverse("finance:home")


def _index_filename(trading_acc_username: str) -> str:
    return f"Index_{trading_acc_username}.htm"


def _user_owns_account(user, account: TradingAccount) -> bool:
    if user.is_superuser:
        return True
    return account.users.filter(pk=user.pk).exists()


def _accounts_for_user(user):
    """Superusers see every trading account; others only linked ones."""
    if user.is_superuser:
        return TradingAccount.objects.all()
    return user.trading_accounts.all()


def _resolve_index_name(trading_acc_username: str) -> str | None:
    """Return Index filename if history files exist for this account."""
    files = scan_account_history(trading_acc_username)
    if not files:
        return None
    index_name = _index_filename(trading_acc_username)
    if safe_resolve_history(trading_acc_username, index_name):
        return index_name
    index_files = [f for f in files if f.report_type == "index"]
    if index_files:
        return index_files[0].filename
    return None


def _load_history_html(trading_acc_username: str, filename: str) -> str:
    path = safe_resolve_history(trading_acc_username, filename)
    if path is None:
        raise Http404("فایل تاریخچه یافت نشد")
    html = read_history_html(path)
    report_type = classify_filename(filename, trading_acc_username)

    if report_type == "index":
        html = rewrite_index_hrefs(html, trading_acc_username, _file_url)
        html = ensure_index_home_button(html, _home_url())
    else:
        # Return control on Daily/Weekly/… goes back to this account's Index
        index_name = _resolve_index_name(trading_acc_username) or _index_filename(
            trading_acc_username
        )
        html = rewrite_home_button(html, _file_url(index_name), target="_self")
    return html


def _render_missing_history(request, account: TradingAccount, message: str):
    return render(
        request,
        "finance/missing.html",
        {
            "title": "فایل تاریخچه یافت نشد",
            "message": message,
            "show_create": False,
            "accounts": _accounts_for_user(request.user),
            "active_account": account,
        },
    )


def _open_account_index(request, account: TradingAccount):
    """
    Open the account Index as a standalone .htm page (no portal chrome).
    Used when navigating to /history/accounts/<id>/ directly.
    """
    acc = account.trading_acc_username
    index_name = _resolve_index_name(acc)
    if index_name is None:
        files = scan_account_history(acc)
        if not files:
            return _render_missing_history(
                request,
                account,
                f"فایل‌های تاریخچه برای حساب «{acc}» پیدا نشد.",
            )
        return _render_missing_history(
            request,
            account,
            f"فایل فهرست تاریخچه برای حساب «{acc}» پیدا نشد.",
        )
    return redirect("finance:history_file", filename=index_name)


def home_view(request):
    """Legacy /home/ — redirect to public Main."""
    return redirect("account:home")


def finance_hub_view(request):
    """Public finance hub with link into History."""
    return render(request, "finance/hub.html")


@login_required
@require_GET
def history_index_view(request):
    accounts = list(_accounts_for_user(request.user))
    if not accounts:
        return render(
            request,
            "finance/missing.html",
            {
                "title": "حساب ترید یافت نشد",
                "message": "حساب تریدی یافت نشد.",
                "show_create": True,
                "accounts": [],
                "active_account": None,
            },
        )

    # Enrich with Index URLs for new-tab links
    account_rows = []
    for account in accounts:
        index_name = _resolve_index_name(account.trading_acc_username)
        account_rows.append(
            {
                "account": account,
                "index_url": _file_url(index_name) if index_name else None,
                "detail_url": reverse("finance:history_account", kwargs={"pk": account.pk}),
            }
        )

    return render(
        request,
        "finance/accounts.html",
        {
            "accounts": accounts,
            "account_rows": account_rows,
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
            return redirect("finance:index")

        account = TradingAccount.objects.create(
            trading_acc_username=acc_username,
            broker=broker,
        )
        account.users.add(request.user)
        ensure_history_dir(acc_username)
        messages.success(request, "حساب ترید با موفقیت ایجاد شد.")
        return redirect("finance:index")

    return render(
        request,
        "finance/trading_account_form.html",
        {
            "form": form,
            "accounts": _accounts_for_user(request.user),
        },
    )


@login_required
@require_GET
def history_account_view(request, pk: int):
    account = get_object_or_404(TradingAccount, pk=pk)
    if not _user_owns_account(request.user, account):
        raise Http404("حساب ترید یافت نشد")
    return _open_account_index(request, account)


@login_required
@require_GET
def history_file_view(request, filename: str):
    """Serve history HTML as a standalone page (no portal chrome)."""
    account = _resolve_account_for_file(request.user, filename)
    if account is None:
        raise Http404("فایل تاریخچه یافت نشد")
    html = _load_history_html(account.trading_acc_username, filename)
    return HttpResponse(html, content_type="text/html; charset=utf-8")


def _resolve_account_for_file(user, filename: str):
    """Find which trading account owns this history filename (all for superuser)."""
    for account in _accounts_for_user(user):
        if classify_filename(filename, account.trading_acc_username):
            if safe_resolve_history(account.trading_acc_username, filename):
                return account
    return None
