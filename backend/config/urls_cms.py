"""Reserved for Phase 2: the CMS API used by the Next.js admin interface.

In Phase 1 the CMS is Django Admin (/admin/), which does not need an API.
Keep CMS serializers separate from the public ones so admin-only fields can never leak.
"""
urlpatterns = []
