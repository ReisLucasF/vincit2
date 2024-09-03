# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ---- example index page ----
@auth.requires_login()
def index():
    return dict()

# ---- Action for login/register/etc (required for auth) -----

def user():
    return dict(form=auth())


# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    return response.download(request, db)
