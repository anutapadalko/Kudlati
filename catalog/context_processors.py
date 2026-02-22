from .models import ProductLike

SESSION_KEY = "liked_product_ids"


def _session_likes(request):
    raw = request.session.get(SESSION_KEY, [])
    ids = set()
    for x in raw:
        try:
            ids.add(int(x))
        except (TypeError, ValueError):
            pass
    return ids


def likes_context(request):
    if request.user.is_authenticated:
        ids = set(
            ProductLike.objects.filter(user=request.user)
            .values_list("product_id", flat=True)
        )
    else:
        ids = _session_likes(request)

    return {
        "liked_ids": ids,
        "liked_count": len(ids),
    }