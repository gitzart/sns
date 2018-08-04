from datetime import datetime, timedelta

import pytest

from sqlalchemy.orm.query import Query

from project.api.models.user import Follower, Friendship, User
from project.api.models.enums import FriendshipState


ACCEPTED, BLOCKED, PENDING, SUGGESTED = FriendshipState.__members__.values()


class TestFriendshipModel:
    def test_friendship_get_returns_query(self, db):
        assert isinstance(Friendship.get(1, 2), Query)

    def test_friendship_build(self, setup, db):
        db.session.add_all(Friendship.build(1, 2, 1, ACCEPTED))
        db.session.commit()

        data = Friendship.get(1, 2).all()
        assert data[0].left_user_id == 1
        assert data[0].right_user_id == 2

        assert data[1].left_user_id == 2
        assert data[1].right_user_id == 1

        for i in range(2):
            assert data[i].action_user_id == 1
            assert data[i].state == ACCEPTED

    def test_friendship_update(self, setup, db):
        data = Friendship.build(1, 2, 1, ACCEPTED)
        db.session.add_all(data)
        db.session.commit()

        Friendship.update(data, 2, BLOCKED)
        db.session.commit()

        data = Friendship.get(1, 2).all()
        for i in range(2):
            assert data[i].action_user_id == 2
            assert data[i].state == BLOCKED

    def test_friendship_delete_returns_2(self, setup, db):
        db.session.add_all(Friendship.build(1, 2, 1, ACCEPTED))
        db.session.commit()
        assert Friendship.delete(1, 2) == 2

    def test_friendship_ondelete_cascade(self, setup, db):
        db.session.add_all(Friendship.build(1, 2, 3, SUGGESTED))
        db.session.commit()
        assert Friendship.get(1, 2).count() == 2

        User.query.filter_by(id=3).delete(synchronize_session=False)
        db.session.commit()
        assert Friendship.get(1, 2).count() == 0


class TestFollowerModel:
    def test_follower_delete_returns_1(self, setup, db):
        db.session.add(Follower(follower_id=1, followed_id=2))
        db.session.commit()
        assert Follower.delete(1, 2) == 1

    def test_follower_ondelete_cascade(self, setup, db):
        db.session.add(Follower(follower_id=1, followed_id=2))
        db.session.commit()
        assert Follower.query.get((1, 2)) is not None

        User.query.filter_by(id=2).delete(synchronize_session=False)
        db.session.commit()
        assert Follower.query.get((1, 2)) is None


@pytest.mark.usefixtures('setup')
class TestUserModel:
    def test_user_property_friendship_returns_user_instance(self, db):
        db.session.add_all(Friendship.build(4, 5, 5, BLOCKED))
        db.session.commit()

        song = User.query.get(5)
        bill = song.friendship.first()
        assert isinstance(bill, User)
        assert bill.first_name == 'bill'

    def test_user_property_followers_and_followings_return_user_instance(
            self, db):
        db.session.add(Follower(follower_id=4, followed_id=5))
        db.session.add(Follower(follower_id=5, followed_id=4))
        db.session.commit()

        bill, song = User.query.filter(User.id.in_([4, 5])).all()
        follower_user = bill.followers.first()
        followed_user = bill.followings.first()

        assert isinstance(follower_user, User)
        assert isinstance(followed_user, User)
        assert follower_user.first_name == 'song'
        assert followed_user.first_name == 'song'

    def test__get_by_id__pass(self, db):
        amy_id = 2
        amy = User.get_by_id(amy_id)
        assert amy is not None
        assert amy.first_name == 'amy'

    def test__get_by_id__fail_invalid_ID_nondigit_str(self, db):
        uid = 'invalid_ID'
        with pytest.raises(Exception) as e:
            User.get_by_id(uid)
        assert 'invalid ID' in str(e.value)

    def test__get_by_id__fail_invalid_ID_None_type(self, db):
        uid = None
        with pytest.raises(Exception) as e:
            User.get_by_id(uid)
        assert 'invalid ID' in str(e.value)

    def test__get_by_id__fail_invalid_ID_empty_str(self, db):
        uid = None
        with pytest.raises(Exception) as e:
            User.get_by_id(uid)
        assert 'invalid ID' in str(e.value)

    def test_user_mutual_friends_returns_query(self, db):
        assert isinstance(User.mutual_friends(1, 2), Query)

    def test_user_mutual_friends_returns_2_user_instances(self, db):
        db.session.add_all(Friendship.build(1, 2, 1, ACCEPTED))
        db.session.add_all(Friendship.build(1, 3, 1, ACCEPTED))
        db.session.add_all(Friendship.build(1, 4, 1, ACCEPTED))
        db.session.add_all(Friendship.build(1, 5, 1, ACCEPTED))
        db.session.add_all(Friendship.build(2, 3, 2, ACCEPTED))
        db.session.add_all(Friendship.build(2, 4, 2, ACCEPTED))
        db.session.add_all(Friendship.build(2, 5, 2, PENDING))
        db.session.commit()

        users = User.mutual_friends(1, 2).all()
        assert len(users) == 2
        assert isinstance(users[0], User)
        assert users[0].first_name == 'doctor'

    def test_user_is_friend(self, db):
        db.session.add_all(Friendship.build(3, 4, 3, ACCEPTED))
        db.session.add_all(Friendship.build(3, 5, 3, PENDING))
        db.session.commit()

        doctor = User.query.get(3)
        assert doctor.is_friend(4)
        assert not doctor.is_friend(5)

    def test_user_is_following(self, db):
        db.session.add(Follower(follower_id=5, followed_id=1))
        db.session.commit()

        rory, song = User.query.filter(User.id.in_([1, 5])).all()
        assert song.is_following(rory.id)
        assert not rory.is_following(song.id)

    def test_user_is_mutual_friend_of(self, db):
        db.session.add_all(Friendship.build(2, 3, 2, ACCEPTED))
        db.session.add_all(Friendship.build(2, 4, 2, ACCEPTED))
        db.session.commit()

        amy = User.query.get(2)
        assert amy.is_mutual_firend_of(3, 4)
        assert not amy.is_mutual_firend_of(3, 5)

    def test_user_suggest_passes(self, db):
        db.session.add_all(Friendship.build(3, 4, 3, ACCEPTED))
        db.session.add_all(Friendship.build(3, 5, 3, ACCEPTED))
        db.session.commit()

        doctor = User.query.get(3)
        db.session.add_all(doctor.suggest(4, 5))
        db.session.commit()
        assert Friendship.get(4, 5).filter_by(state=SUGGESTED).count() == 2

    def test_user_suggest_fails(self, db):
        bill = User.query.get(4)
        assert bill.suggest(3, 5) is None

    def test_user_send_friend_request_new_request_passes(self, db):
        song = User.query.get(5)
        db.session.add_all(song.send_friend_request(1))
        db.session.commit()
        assert Friendship.get(1, 5).filter_by(state=PENDING).count() == 2

    def test_user_send_friend_request_update_from_suggested_friendship_passes(
            self, db):
        db.session.add_all(Friendship.build(1, 3, 2, SUGGESTED))
        db.session.commit()

        rory = User.query.get(1)
        rory.send_friend_request(3)
        db.session.commit()
        assert Friendship.get(1, 3).filter_by(state=PENDING).count() == 2

    def test_user_send_friend_request_fails(self, db):
        db.session.add_all(Friendship.build(2, 3, 2, BLOCKED))
        db.session.commit()

        amy = User.query.get(2)
        assert amy.send_friend_request(3) is None

    def test_user_accept_passes(self, db):
        db.session.add_all(Friendship.build(4, 3, 4, PENDING))
        db.session.commit()

        doctor = User.query.get(3)
        doctor.accept(4)
        db.session.commit()
        assert Friendship.get(3, 4).filter_by(state=ACCEPTED).count() == 2

    def test_user_accept_same_user_policy_fails(self, db):
        """Send friend request or accept, people can do only one at a time,
        not both.
        """
        db.session.add_all(Friendship.build(3, 4, 3, PENDING))
        db.session.commit()

        doctor = User.query.get(3)
        assert doctor.accept(4) is None

    def test_user_accept_fails(self, db):
        db.session.add_all(Friendship.build(3, 4, 4, ACCEPTED))
        db.session.commit()

        doctor = User.query.get(3)
        assert doctor.accept(4) is None

    def test_user_block_passes(self, db):
        bill = User.query.get(4)
        db.session.add_all(bill.block(5))
        db.session.commit()
        assert Friendship.get(4, 5).filter_by(state=BLOCKED).count() == 2

    def test_user_block_friend_passes(self, db):
        db.session.add_all(Friendship.build(4, 5, 4, ACCEPTED))
        db.session.commit()

        bill = User.query.get(4)
        bill.block(5)
        db.session.commit()
        assert Friendship.get(4, 5).filter_by(state=BLOCKED).count() == 2

    def test_user_block_already_blocked_user_fails(self, db):
        db.session.add_all(Friendship.build(5, 1, 5, BLOCKED))
        db.session.commit()

        song = User.query.get(5)
        assert song.block(1) is None

    def test_user_unblock_same_user_policy_passes(self, db):
        """Block or unblock can be done only by the same person."""
        db.session.add_all(Friendship.build(1, 2, 1, BLOCKED))
        db.session.commit()

        rory = User.query.get(1)
        rory.unblock(2)
        db.session.commit()
        assert Friendship.get(1, 2).count() == 0

    def test_user_unblock_same_user_policy_fails(self, db):
        """Block or unblock can be only done by the same person."""
        db.session.add_all(Friendship.build(2, 3, 3, BLOCKED))
        db.session.commit()

        amy = User.query.get(2)
        assert amy.unblock(3) is None

    def test_user_unblock_fails(self, db):
        doctor = User.query.get(3)
        assert doctor.unblock(4) is None

    def test_user_unfriend_passes(self, db):
        db.session.add_all(Friendship.build(4, 5, 4, ACCEPTED))
        db.session.commit()

        bill = User.query.get(4)
        bill.unfriend(5)
        db.session.commit()
        assert Friendship.get(4, 5).count() == 0

    def test_user_unfriend_fails(self, db):
        song = User.query.get(5)
        assert song.unfriend(1) is None

    def test_user_decline_friend_request_passes(self, db):
        db.session.add_all(Friendship.build(1, 2, 2, PENDING))
        db.session.commit()

        rory = User.query.get(1)
        rory.decline_friend_request(2)
        db.session.commit()
        assert Friendship.get(1, 2).count() == 0

    def test_user_decline_friend_request_fails(self, db):
        db.session.add_all(Friendship.build(2, 3, 2, ACCEPTED))
        db.session.commit()

        amy = User.query.get(2)
        assert amy.decline_friend_request(3) is None

    def test_user_follow_passes(self, db):
        doctor = User.query.get(3)
        db.session.add(doctor.follow(4))
        db.session.commit()
        assert Follower.query.get((3, 4)) is not None
        assert Follower.query.get((4, 3)) is None

    def test_user_follow_blocked_user_fails(self, db):
        db.session.add_all(Friendship.build(4, 5, 5, BLOCKED))
        db.session.commit()

        bill = User.query.get(4)
        assert bill.follow(5) is None

    def test_user_follow_already_followed_user_fails(self, db):
        db.session.add(Follower(follower_id=5, followed_id=1))
        db.session.commit()

        song = User.query.get(5)
        assert song.follow(1) is None

    def test_user_unfollow_passes(self, db):
        db.session.add(Follower(follower_id=1, followed_id=2))
        db.session.commit()

        rory = User.query.get(1)
        rory.unfollow(2)
        db.session.commit()
        assert Follower.query.get((1, 2)) is None

    def test_user_unfollow_fails(self, db):
        amy = User.query.get(2)
        assert amy.unfollow(2) is None

    def test_user_snooze_passes(self, db):
        db.session.add(Follower(follower_id=3, followed_id=4))
        db.session.commit()

        doctor = User.query.get(3)
        doctor.snooze(4)
        db.session.commit()

        data = Follower.query.get((3, 4))
        assert data.is_snoozed
        assert data.expiration > datetime.utcnow()

    def test_user_snooze_already_snoozed_user_fails(self, db):
        data = Follower(
            follower_id=4,
            followed_id=5,
            is_snoozed=True,
            expiration=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(data)
        db.session.commit()

        bill = User.query.get(4)
        assert bill.snooze(5) is None

    def test_user_snooze_fails(self, db):
        bill = User.query.get(4)
        assert bill.snooze(5) is None

    def test_user_unsnooze_passes(self, db):
        data = Follower(
            follower_id=5,
            followed_id=1,
            is_snoozed=True,
            expiration=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(data)
        db.session.commit()

        song = User.query.get(5)
        song.unsnooze(1)
        db.session.commit()

        data = Follower.query.get((5, 1))
        assert not data.is_snoozed
        assert data.expiration is None

    def test_user_unsnooze_fails(self, db):
        db.session.add(Follower(follower_id=1, followed_id=2))
        db.session.commit()

        rory = User.query.get(1)
        assert rory.unsnooze(2) is None

    def test_user_ondelete_cascade(self, db):
        db.session.add_all(Friendship.build(2, 3, 4, SUGGESTED))
        db.session.add_all(Friendship.build(2, 5, 2, ACCEPTED))
        db.session.add(Follower(follower_id=2, followed_id=3))
        db.session.add(Follower(follower_id=2, followed_id=5))
        db.session.add(Follower(follower_id=3, followed_id=2))
        db.session.add(Follower(follower_id=4, followed_id=2))
        db.session.commit()

        assert Friendship.query.count() == 4
        assert Follower.query.count() == 4

        User.query.filter_by(id=2).delete(synchronize_session=False)
        db.session.commit()

        assert Friendship.query.count() == 0
        assert Follower.query.count() == 0
