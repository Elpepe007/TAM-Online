instructions = [
"""
  CREATE TABLE IF NOT EXISTS user (
      id INT AUTO_INCREMENT PRIMARY KEY,
      username VARCHAR(255) NOT NULL,
      password VARCHAR(255) NOT NULL,
      user_type ENUM('profesor', 'estudiante')
);
""",
"""
  CREATE TABLE IF NOT EXISTS talleres (
      id INT AUTO_INCREMENT PRIMARY KEY,
      nombre VARCHAR(255) NOT NULL
  );
""",
"""
  CREATE TABLE IF NOT EXISTS profesores (
      id INT AUTO_INCREMENT PRIMARY KEY,
      user_id INT,
      taller_id INT,
      FOREIGN KEY (user_id) REFERENCES user(id),
      FOREIGN KEY (taller_id) REFERENCES talleres(id)
);
""",
"""
  CREATE TABLE IF NOT EXISTS alumnos (
      id INT AUTO_INCREMENT PRIMARY KEY,
      taller_id INT,
      nombre VARCHAR(255) NOT NULL,
      horas TIME,
      FOREIGN KEY (taller_id) REFERENCES talleres(id)
  );
"""
]
