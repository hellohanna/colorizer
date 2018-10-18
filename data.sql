
CREATE TABLE users
    (
        user_id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255),
        password VARCHAR(255)
    );
    
INSERT INTO users (name, email, password) VALUES ('Jane', 'jdoe@gmail.com', '1234');
INSERT INTO users (name, email, password) VALUES ('Alice', 'aperson@hotmail.com', '2134');
INSERT INTO users (name, email, password) VALUES ('Bob', 'bpersonne@yahoo.com', 'qwerty');


CREATE TABLE photos
  (
     photo_id SERIAL PRIMARY KEY,
     user_id INT NOT NULL,
     original_photo VARCHAR(300),
     processed_photo VARCHAR(300),
     FOREIGN KEY (user_id) REFERENCES users(user_id)
  );

INSERT INTO photos (user_id, original_photo, processed_photo) VALUES (1, 'kingfisher-1905255.jpg', 'kingfisher-1905255.jpg');
INSERT INTO photos (user_id, original_photo, processed_photo) VALUES (2, 'kingfisher-1905255.jpg', 'kingfisher-1905255.jpg');
INSERT INTO photos (user_id, original_photo, processed_photo) VALUES (3, 'kingfisher-1905255.jpg', 'kingfisher-1905255.jpg');
