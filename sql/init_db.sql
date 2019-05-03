/*
* Script to initialize the database.
* Adds a single, active semester
* and an admin user with the password 'admin'
*/
INSERT INTO user VALUES (
    'admin',
    0x5a38afb1a18d408e6cd367f9db91e2ab9bce834cdad3da24183cc174956c20ce35dd39c2bd36aae907111ae3d6ada353f7697a5f1a8fc567aae9e4ca41a9d19d,
    800000001,
    'admin',
    NULL
);

INSERT INTO semester VALUES (
    'FALL',
    2019,
    'yes'
);
