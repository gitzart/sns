import pytest

from datetime import datetime, timedelta

from ..api.models.user import User, Friendship, Follower


def create_users(db, *names):
    users = []
    for name in names:
        users.append(User(name))
    db.session.add_all(users)
    db.session.commit()
    return users


def set_expiration(days=0):
    return datetime.utcnow() + timedelta(days=days)


class TestFriendshipModel:
    def test_build_friendship(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        r1, r2 = Friendship.build(alan, karen, alan, 'friend')
        db.session.commit()

        r1, r2 = Friendship.get(alan, karen).all()

        # alan => karen
        assert r1.left_user == alan
        assert r1.right_user == karen
        assert r1.action_user == alan
        assert r1.type == 'friend'

        # karen => alan
        assert r2.left_user == karen
        assert r2.right_user == alan
        assert r2.action_user == alan
        assert r2.type == 'friend'

    def test_update_friendship(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        r1, r2 = Friendship.build(alan, karen, alan, 'friend')
        db.session.commit()

        r1, r2 = Friendship.update(alan, karen, alan, 'block')
        db.session.commit()

        for rv in Friendship.get(alan, karen).all():
            assert rv.type == 'block'

    def test_update_friendship_lazy(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        r1, r2 = Friendship.update(alan, karen, alan, 'block', lazy=True)
        db.session.commit()

        for rv in Friendship.get(alan, karen).all():
            assert rv.type == 'block'

    def test_destroy_friendship(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        assert Friendship.destroy(alan, karen) == 0
        db.session.commit()

        r1, r2 = Friendship.build(alan, karen, alan, 'friend')
        db.session.commit()

        Friendship.destroy(alan, karen)
        db.session.commit()

        assert Friendship.query.count() == 0


class TestFollowerModel:
    def test_build_follower(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        # alan follows karen
        Follower.build(alan, karen)
        db.session.commit()
        assert Follower.query.count() == 1
        rv = Follower.query.get((alan.id, karen.id))
        assert rv.follower == alan
        assert rv.followed == karen

        # karen follows alan
        Follower.build(karen, alan)
        db.session.commit()
        assert Follower.query.count() == 2
        rv = Follower.query.get((karen.id, alan.id))
        assert rv.follower == karen
        assert rv.followed == alan

    def test_build_follower_mutual(self, db):
        alan = User('alan')
        karen = User('karen')
        db.session.add_all([alan, karen])
        db.session.commit()

        # follow mutually
        r1, r2 = Follower.build(alan, karen, mutual=True)
        db.session.commit()

        rv = Follower.get(alan, karen, mutual=True).all()
        assert len(rv) == 2
        assert rv[0] == r1
        assert rv[1] == r2

    def test_update_follower(self, db):
        alan, karen = create_users(db, 'alan', 'karen')
        Follower.build(alan, karen)
        db.session.commit()

        # alan snoozes karen
        Follower.update(alan, karen, expiration=set_expiration(30))
        db.session.commit()

        assert Follower.get(alan, karen).filter(
            Follower.expiration is not None
        ).count() > 0

    def test_update_follower_lazy(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        # alan follows karen
        Follower.update(alan, karen, lazy=True)
        db.session.commit()

        assert Follower.get(alan, karen).count() == 1

    def test_update_follower_mutual_pass(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        # mutually follows
        Follower.build(alan, karen)
        Follower.build(karen, alan)
        db.session.commit()

        # mutually snooze
        Follower.update(alan, karen, set_expiration(30), mutual=True)
        db.session.commit()

        rv = Follower.get(alan, karen, mutual=True).all()
        assert len(rv) == 2
        assert rv[0].follower == alan
        assert rv[0].expiration is not None
        assert rv[1].follower == karen
        assert rv[1].expiration is not None

    def test_update_follower_mutual_fail(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        # alan follows karen
        Follower.build(alan, karen)
        db.session.commit()

        # alan snoozes karen
        with pytest.raises(ValueError):
            Follower.update(alan, karen, set_expiration(30), mutual=True)

    def test_destroy_follower(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        assert Follower.destroy(alan, karen) == 0
        db.session.commit()

        Follower.build(alan, karen)
        db.session.commit()

        Follower.destroy(alan, karen)
        assert Follower.get(alan, karen).count() == 0


class TestUserModel:
    def test_is_friend(self, db):
        alan, karen = create_users(db, 'alan', 'karen')
        assert not alan.is_friend(karen)

        # make friends
        Friendship.build(alan, karen, alan, 'friend')
        db.session.commit()

        assert alan.is_friend(karen)
        assert karen.is_friend(alan)

    def test_is_mutual_friend(self, db):
        alan, karen, rory = create_users(db, 'alan', 'karen', 'rory')
        assert not alan.is_mutual_firend(karen, rory)

        # make friends
        Friendship.build(alan, karen, alan, 'friend')
        Friendship.build(alan, rory, alan, 'friend')
        Friendship.build(karen, rory, karen, 'friend')
        db.session.commit()

        assert alan.is_mutual_firend(karen, rory)
        assert karen.is_mutual_firend(alan, rory)

    def test_is_following(self, db):
        alan, karen = create_users(db, 'alan', 'karen')
        assert not alan.is_following(karen)

        # alan follows karen
        Follower.build(alan, karen)
        db.session.commit()

        assert alan.is_following(karen)
        assert not karen.is_following(alan)

    def test_is_snoozing(self, db):
        alan, karen = create_users(db, 'alan', 'karen')
        assert not alan.is_snoozing(karen)

        # start snoozing
        Follower.build(alan, karen, expiration=set_expiration(30))
        db.session.commit()

        assert alan.is_following(karen)
        assert alan.is_snoozing(karen)
        assert not karen.is_snoozing(alan)

        # snoozing expired
        Follower.update(alan, karen, expiration=set_expiration())
        db.session.commit()

        assert not alan.is_snoozing(karen)

    def test_suggest(self, db):
        alan, karen, rory = create_users(db, 'alan', 'karen', 'rory')

        # karen must be the mutual friend to suggest
        assert karen.suggest(alan, rory) is None
        db.session.commit()
        assert Friendship.get(alan, rory).count() == 0

        # alan friended karen
        Friendship.build(alan, karen, alan, 'friend')
        # rory friended karen
        Friendship.build(rory, karen, rory, 'friend')
        db.session.commit()

        # karen can suggest alan and rory as they are not friends yet
        assert karen.is_mutual_firend(alan, rory)
        r1, r2 = karen.suggest(alan, rory)
        db.session.commit()

        rv = Friendship.get(alan, rory).all()
        assert len(rv) == 2
        assert rv[0] == r1
        assert rv[1] == r2

        # suggestion is pending, karen cannot suggest again
        assert karen.suggest(alan, rory) is None

    def test_make_friends(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        # alan sent request the first time
        alan.make_friends(karen)
        db.session.commit()

        # request is pending, cannot be sent again
        assert alan.make_friends(karen) is None

        rv = Friendship.get(alan, karen).filter_by(type='pending').first()
        assert rv.action_user == alan
        assert rv.left_user == alan
        assert rv.right_user == karen

    def test_accept(self, db):
        alan, karen, rory = create_users(db, 'alan', 'karen', 'rory')

        # send friend requests
        alan.make_friends(karen)
        rory.make_friends(alan)
        db.session.commit()

        # alan cannot accept the request he made
        assert alan.accept(karen) is None
        db.session.commit()
        assert not karen.is_friend(alan)

        # requests accepted
        karen.accept(alan)
        alan.accept(rory)
        db.session.commit()

        assert alan.friends.count() == 2
        assert karen.is_friend(alan)
        assert rory.is_friend(alan)

    def test_follow_on_accept(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        # alan friended karen
        alan.make_friends(karen)
        db.session.commit()
        karen.accept(alan)
        db.session.commit()

        # when request accepted, users become followers
        # to each other
        assert karen.is_following(alan)
        assert alan.is_following(karen)

    def test_block(self, db):
        alan, karen, rory = create_users(db, 'alan', 'karen', 'rory')

        assert alan.block(karen) is not None
        assert rory.block(alan) is not None
        db.session.commit()

        # rory already blocked alan. alan cannot block rory
        assert alan.block(rory) is None
        # alan already blocked karen
        assert alan.block(karen) is None

    def test_unblock(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        # alan has never blocked karen
        assert alan.unblock(karen) is None

        alan.block(karen)
        db.session.commit()
        assert alan.unblock(karen) is not None
        db.session.commit()

        # once unblocked, they are no longer in any relationship
        assert Friendship.query.count() == 0

    def test_unfriend(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        # alan can only unfriend his friend
        assert alan.unfriend(karen) is None

        # become friends
        alan.make_friends(karen)
        db.session.commit()
        karen.accept(alan)
        db.session.commit()
        assert karen.is_friend(alan)

        # alan unfriends karen
        assert alan.unfriend(karen) is not None
        db.session.commit()

        assert Friendship.query.count() == 0

    def test_decline(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        # cannot decline when there is no requests
        assert alan.decline(karen) is None

        # karen makes friend request
        karen.make_friends(alan)
        db.session.commit()

        # alan declines
        assert alan.decline(karen) is not None
        db.session.commit()

        assert Friendship.query.count() == 0

    def test_get_mutual_friends(self, db):
        alan, karen, rory = create_users(db, 'alan', 'karen', 'rory')

        # no friend relationships, hence no mutual friends
        assert User.mutual_friends(rory, karen).count() == 0

        # make friends
        alan.make_friends(karen)
        alan.make_friends(rory)
        db.session.commit()

        # accept requests
        karen.accept(alan)
        rory.accept(alan)

        assert User.mutual_friends(rory, karen).first() == alan

    def test_follow(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        assert alan.follow(karen) is not None
        db.session.commit()

        # alan has already followed karen
        assert alan.follow(karen) is None

        assert Follower.query.count() == 1

    def test_unfollow(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        # has to follow karen first before unfollow
        assert alan.unfollow(karen) is None

        alan.follow(karen)
        db.session.commit()
        assert alan.is_following(karen)

        alan.unfollow(karen)
        db.session.commit()
        assert not alan.is_following(karen)

    def test_snooze(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        # first follow, then snooze
        assert alan.snooze(karen) is None

        alan.follow(karen)
        db.session.commit()
        alan.snooze(karen)
        db.session.commit()
        assert alan.is_snoozing(karen)

        # alan has already snoozed karen
        assert alan.snooze(karen) is None

    def test_unsnooze(self, db):
        alan, karen = create_users(db, 'alan', 'karen')

        # first snooze, then unsnooze
        assert alan.unsnooze(karen) is None

        alan.follow(karen)
        db.session.commit()
        alan.snooze(karen)
        db.session.commit()
        assert alan.is_snoozing(karen)

        assert alan.unsnooze(karen) is not None
        db.session.commit()

        # now, alan is not snoozing
        assert not alan.is_snoozing(karen)
        # but still following
        assert alan.is_following(karen)
