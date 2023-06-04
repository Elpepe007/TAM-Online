instructions = [
    'SET FOREIGN_KEY_CHECKS=0;',
    'DROP TABLE IF EXISTS profesores;',
    'DROP TABLE IF EXISTS user;',
    'DROP TABLE IF EXISTS talleres;',
    'DROP TABLE IF EXISTS alumnos;',         
    'SET FOREIGN_KEY_CHECKS=1;',
"""
  CREATE TABLE user (
      id INT AUTO_INCREMENT PRIMARY KEY,
      username VARCHAR(255) NOT NULL,
      password VARCHAR(255) NOT NULL,
      user_type ENUM('profesor', 'estudiante')
);
""",
"""
  CREATE TABLE talleres (
      id INT AUTO_INCREMENT PRIMARY KEY,
      nombre VARCHAR(255) NOT NULL
  );
""",
"""
  CREATE TABLE profesores (
      id INT AUTO_INCREMENT PRIMARY KEY,
      user_id INT,
      taller_id INT,
      FOREIGN KEY (user_id) REFERENCES user(id),
      FOREIGN KEY (taller_id) REFERENCES talleres(id)
);
""",
"""
  CREATE TABLE alumnos (
      id INT AUTO_INCREMENT PRIMARY KEY,
      taller_id INT,
      nombre VARCHAR(255) NOT NULL,
      horas DECIMAL(5, 2),
      FOREIGN KEY (taller_id) REFERENCES talleres(id)
  );
"""
]
