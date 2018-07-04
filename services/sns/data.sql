INSERT INTO users (first_name, last_name, email, password, gender, created_at, marital_status) VALUES
('amy', 'pond', 'amy@email.com', 'amyspassword', 'female', '2016-05-08 12:23:57.41017', 'single'),
('bill', 'potts', 'bill@email.com', 'billspassword', 'female', '2016-05-08 12:27:13.520557', 'single'),
('doctor', 'who', 'doctor@email.com', 'doctorspassword', 'others', '2017-05-09 17:05:46.000723', 'married'),
('rory', 'williams', 'rory@email.com', 'roryspassword', 'male', '2018-02-09 17:09:02.634509', 'single'),
('rose', 'tyler', 'rose@email.com', 'rosespassword', 'female', '2018-03-08 07:23:26.47011', 'married'),
('dalek', 'thay', 'dalek@email.com', 'dalekspassword', 'others', '2018-05-09 16:42:35.801206', 'open relationship'),
('angel', 'statue', 'angel@email.com', 'angelspassword', 'others', '2018-05-10 19:53:42.086208', 'open relationship'),
('song', 'river', 'song@email.com', 'songspassword', 'female', '2018-05-11 16:53:52.57197', 'married'),
('clara', 'oswald', 'clara@email.com', 'claraspassword', 'female', '2018-05-12 17:03:21.759576', 'taken'),
('danny', 'pink', 'danny@email.com', 'dannyspassword', 'male', '2018-05-15 20:23:21.759576', 'taken'),
('cyber', 'mat', 'cyber@email.com', 'cyberspassword', 'others', '2018-05-19 23:13:12.057208', 'complicated');

INSERT INTO friendships (left_user_id, right_user_id, action_user_id, state, created_at) VALUES
(1, 2, 2, 'accepted', '2016-05-08 12:27:13.520557'),
(2, 1, 2, 'accepted', '2016-05-08 12:27:13.520557'),
(1, 3, 3, 'accepted', '2017-05-09 17:05:46.000723'),
(3, 1, 3, 'accepted', '2017-05-09 17:05:46.000723'),
(1, 4, 1, 'pending', '2018-02-09 17:09:02.634509'),
(4, 1, 1, 'pending', '2018-02-09 17:09:02.634509'),
(10, 1, 10, 'pending', '2018-05-19 23:13:12.057208'),
(1, 10, 10, 'pending', '2018-05-19 23:13:12.057208'),
(3, 9, 9, 'accepted', '2018-05-12 17:03:21.759576'),
(9, 3, 9, 'accepted', '2018-05-12 17:03:21.759576'),
(1, 9, 3, 'suggested', '2018-05-12 17:03:21.759576'),
(9, 1, 3, 'suggested', '2018-05-12 17:03:21.759576'),
(3, 2, 2, 'accepted', '2017-08-09 17:05:46.000723'),
(2, 3, 2, 'accepted', '2017-08-09 17:05:46.000723'),
(9, 2, 3, 'suggested', '2018-05-12 17:03:21.759576'),
(2, 9, 3, 'suggested', '2018-05-12 17:03:21.759576'),
(2, 6, 6, 'accepted', '2018-05-09 16:42:35.801206'),
(6, 2, 6, 'accepted', '2018-05-09 16:42:35.801206'),
(1, 6, 2, 'suggested', '2018-05-09 16:42:35.801206'),
(6, 1, 2, 'suggested', '2018-05-09 16:42:35.801206'),
(8, 3, 3, 'accepted', '2018-05-11 16:53:52.57197'),
(3, 8, 3, 'accepted', '2018-05-11 16:53:52.57197'),
(8, 2, 3, 'suggested', '2018-05-11 16:53:52.57197'),
(2, 8, 3, 'suggested', '2018-05-11 16:53:52.57197'),
(8, 1, 3, 'suggested', '2018-05-11 16:53:52.57197'),
(1, 8, 3, 'suggested', '2018-05-11 16:53:52.57197'),
(2, 4, 2, 'blocked', '2018-05-14 09:55:35.995185'),
(2, 5, 2, 'blocked', '2018-05-19 10:55:35.995185'),
(10, 9, 9, 'blocked', '2018-05-23 11:55:35.995185'),
(3, 7, 7, 'blocked', '2018-05-27 12:55:35.995185'),
(5, 6, 5, 'blocked', '2018-06-01 13:55:35.995185'),
(4, 7, 4, 'blocked', '2018-06-05 14:55:35.995185'),
(6, 8, 8, 'blocked', '2018-06-09 15:55:35.995185'),
(7, 6, 6, 'blocked', '2018-06-13 16:55:35.995185'),
(9, 6, 9, 'blocked', '2018-06-17 17:55:35.995185');

INSERT INTO followers (follower_id, followed_id, created_at, is_snoozed, expiration) VALUES
(1, 2, '2018-06-17 17:55:35.995185', 't', '2018-07-17 17:55:35.995185'),
(2, 3, '2018-06-21 18:55:35.995185', 't', '2018-07-21 18:55:35.995185'),
(3, 4, '2018-06-25 19:55:35.995185', 't', '2018-07-25 19:55:35.995185'),
(5, 6, '2018-06-29 20:55:35.995185', 't', '2018-07-29 20:55:35.995185'),
(6, 5, '2018-07-02 21:55:35.995185', 't', '2018-08-02 21:55:35.995185'),
(7, 6, '2018-07-06 22:55:35.995185', 't', '2018-08-06 22:55:35.995185'),
(7, 1, '2018-07-17 23:55:35.995185', 't', '2018-08-17 23:55:35.995185'),
(7, 2, '2018-07-18 00:55:35.995185', 'f', NULL),
(8, 3, '2018-07-19 02:55:35.995185', 'f', NULL),
(9, 4, '2018-07-21 04:55:35.995185', 'f', NULL),
(9, 6, '2018-07-23 05:55:35.995185', 'f', NULL),
(9, 7, '2018-07-24 06:55:35.995185', 'f', NULL),
(10, 3, '2018-07-24 12:55:35.995185', 'f', NULL),
(10, 5, '2018-07-26 14:55:35.995185', 'f', NULL),
(10, 6, '2018-07-26 18:55:35.995185', 'f', NULL);
