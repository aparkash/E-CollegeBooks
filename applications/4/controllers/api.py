# Here go your api methods.


@auth.requires_signature()
def add_post():
    post_id = db.post.insert(
        post_title=request.vars.post_title,
        post_content=request.vars.post_content,
    )
    # We return the id of the new post, so we can insert it along all the others.
    return response.json(dict(post_id=post_id))


def get_post_list():
    results = []
    if auth.user is None:
        # Not logged in.
        rows = db().select(db.post.ALL, orderby=~db.post.post_time)
        for row in rows:
            results.append(dict(
                id=row.id,
                post_title=row.post_title,
                post_content=row.post_content,
                post_author=row.post_author,
                like = False, # Anyway not used as the user is not logged in.
                dislike = False
            ))
    else:
        # Logged in.
        rows = db().select(db.post.ALL, db.user_like.ALL, db.user_dislike.ALL, 
                            left=[
                                db.user_like.on((db.user_like.post_id == db.post.id) & (db.user_like.user_email == auth.user.email)),
                                db.user_dislike.on((db.user_dislike.post_id == db.post.id) & (db.user_dislike.user_email == auth.user.email)),
                            ],
                            orderby=~db.post.post_time)
        for row in rows:
            results.append(dict(
                id=row.post.id,
                post_title=row.post.post_title,
                post_content=row.post.post_content,
                post_author=row.post.post_author,
                like = False if row.user_like.id is None else True,
                dislike = False if row.user_dislike.id is None else True,
            ))
    # For homogeneity, we always return a dictionary.
    return response.json(dict(post_list=results))
    

@auth.requires_signature()
def set_like():
    post_id = int(request.vars.post_id)
    like_status = request.vars.like.lower().startswith('t');
    if like_status:
        db.user_like.update_or_insert(
            (db.user_like.post_id == post_id) & (db.user_like.user_email == auth.user.email),
            post_id = post_id,
            user_email = auth.user.email
        )
    else:
        db((db.user_like.post_id == post_id) & (db.user_like.user_email == auth.user.email)).delete()
    return "ok" # Might be useful in debugging.


def get_likers():
    """Gets the list of people who liked a post."""
    post_id = int(request.vars.post_id)
    # We get directly the list of all the users who liked the post. 
    rows = db(db.user_like.post_id == post_id).select(db.user_like.user_email)
    # If the user is logged in, we remove the user from the set.
    likers_set = set([r.user_email for r in rows])
    if auth.user:
        likers_set -= {auth.user.email}
    likers_list = list(likers_set)
    likers_list.sort()
    # We return this list as a dictionary field, to be consistent with all other calls.
    return response.json(dict(likers=likers_list))

def set_dislike():
    post_id = int(request.vars.post_id)
    dislike_status = request.vars.dislike.lower().startswith('t');
    if dislike_status:
        db.user_dislike.update_or_insert(
            (db.user_dislike.post_id == post_id) & (db.user_dislike.user_email == auth.user.email),
            post_id = post_id,
            user_email = auth.user.email
        )
    else:
        db((db.user_dislike.post_id == post_id) & (db.user_dislike.user_email == auth.user.email)).delete()
    return "ok" # Might be useful in debugging.


def get_dislikers():
    """Gets the list of people who liked a post."""
    post_id = int(request.vars.post_id)
    # We get directly the list of all the users who liked the post. 
    rows = db(db.user_dislike.post_id == post_id).select(db.user_dislike.user_email)
    # If the user is logged in, we remove the user from the set.
    dislikers_set = set([r.user_email for r in rows])
    if auth.user:
        dislikers_set -= {auth.user.email}
    dislikers_list = list(dislikers_set)
    dislikers_list.sort()
    # We return this list as a dictionary field, to be consistent with all other calls.
    return response.json(dict(dislikers=dislikers_list))
