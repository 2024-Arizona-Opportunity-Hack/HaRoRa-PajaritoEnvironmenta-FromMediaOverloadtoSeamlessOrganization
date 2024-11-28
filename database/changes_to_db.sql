-- Add initials column to user table
ALTER TABLE users
ADD COLUMN initials VARCHAR(3);


-- add foreign key constrating of users(user_id) to image_detail and filequeue tabls
ALTER TABLE image_detail
ADD CONSTRAINT fk_user_id
FOREIGN KEY (user_id) REFERENCES users(user_id)
ON DELETE CASCADE;

ALTER TABLE filequeue
ADD CONSTRAINT fk_user_id
FOREIGN KEY (user_id) REFERENCES users(user_id)
ON DELETE CASCADE;

