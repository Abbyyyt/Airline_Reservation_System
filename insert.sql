-- Clear existing data (same as original)
DELETE FROM booking_agent_work_for;
DELETE FROM permission;
DELETE FROM purchases;
DELETE FROM Airline_Staff;
DELETE FROM Customer;
DELETE FROM Booking_agent;
DELETE FROM Ticket;
DELETE FROM Flight;
DELETE FROM Airport;
DELETE FROM Airplane;
DELETE FROM Airline;

-- Insert airlines (more realistic names)
INSERT INTO Airline VALUES ("China Eastern");
INSERT INTO Airline VALUES ("Japan Airlines");
INSERT INTO Airline VALUES ("American Airlines");
INSERT INTO Airline VALUES ("Emirates");
INSERT INTO Airline VALUES ("Singapore Airlines");

-- Insert airports (major international airports)
INSERT INTO Airport VALUES ("JFK", "New York");
INSERT INTO Airport VALUES ("PVG", "Shanghai");
INSERT INTO Airport VALUES ("LAX", "Los Angeles");
INSERT INTO Airport VALUES ("HND", "Tokyo");
INSERT INTO Airport VALUES ("DXB", "Dubai");
INSERT INTO Airport VALUES ("SIN", "Singapore");
INSERT INTO Airport VALUES ("LHR", "London");

-- Insert customers (proper email formats)
INSERT INTO Customer VALUES (
    "alice.wang@email.com", "Alice Wang", 
    "$2b$12$QH7HxpFhSs1G7m5/s7tHK.nsTsztKZj8MjDWW1rtgHHKwp3HQd7qC",  -- Password: "123"
    "5", "Century Avenue", "Shanghai", "China",
    "123333123", "CN12345678", "2029-03-10", "China", "2000-01-01"
);
INSERT INTO Customer VALUES (
    "bob.li@email.com", "Bob Li", 
    "$2b$12$QH7HxpFhSs1G7m5/s7tHK.nsTsztKZj8MjDWW1rtgHHKwp3HQd7qC",  -- Password: "123"
    "2", "Yangsi Road", "Shanghai", "China",
    "123111123", "CN87654321", "2029-03-10", "China", "2001-01-09"
);
INSERT INTO Customer VALUES (
    "john.doe@email.com", "John Doe", 
    "$2b$12$QH7HxpFhSs1G7m5/s7tHK.nsTsztKZj8MjDWW1rtgHHKwp3HQd7qC",  -- Password: "123"
    "123", "Main Street", "New York", "USA",
    "5551234567", "US12345678", "2028-12-31", "USA", "1990-05-15"
);
INSERT INTO Customer VALUES (
    "sarah.smith@email.com", "Sarah Smith", 
    "$2b$12$QH7HxpFhSs1G7m5/s7tHK.nsTsztKZj8MjDWW1rtgHHKwp3HQd7qC",  -- Password: "123"
    "456", "Park Avenue", "Los Angeles", "USA",
    "5559876543", "US87654321", "2030-06-30", "USA", "1985-11-20"
);

-- Insert booking agents (proper email formats)
INSERT INTO Booking_agent VALUES (
    "travel.agent1@agency.com",
    "$2b$12$QH7HxpFhSs1G7m5/s7tHK.nsTsztKZj8MjDWW1rtgHHKwp3HQd7qC",  -- Password: "123"
    "10001"
);
INSERT INTO Booking_agent VALUES (
    "travel.agent2@agency.com",
    "$2b$12$QH7HxpFhSs1G7m5/s7tHK.nsTsztKZj8MjDWW1rtgHHKwp3HQd7qC",  -- Password: "123"
    "10002"
);
INSERT INTO Booking_agent VALUES (
    "global.travel@agency.com",
    "$2b$12$QH7HxpFhSs1G7m5/s7tHK.nsTsztKZj8MjDWW1rtgHHKwp3HQd7qC",  -- Password: "123"
    "10003"
);

-- Insert airplanes (realistic seat counts)
INSERT INTO Airplane VALUES ("China Eastern", "1", "180");
INSERT INTO Airplane VALUES ("China Eastern", "2", "220");
INSERT INTO Airplane VALUES ("Japan Airlines", "3", "250");
INSERT INTO Airplane VALUES ("American Airlines", "4", "200");
INSERT INTO Airplane VALUES ("Emirates", "5", "380");
INSERT INTO Airplane VALUES ("Singapore Airlines", "6", "300");

-- Insert airline staff (proper names & emails)
INSERT INTO Airline_Staff VALUES (
    "jack.goodman@chinaeastern.com", 
    "$2b$12$QH7HxpFhSs1G7m5/s7tHK.nsTsztKZj8MjDWW1rtgHHKwp3HQd7qC",  -- Password: "123"
    "Jack", "Goodman", "1988-02-07", "China Eastern"
);
INSERT INTO Airline_Staff VALUES (
    "john.doe@chinaeastern.com", 
    "$2b$12$QH7HxpFhSs1G7m5/s7tHK.nsTsztKZj8MjDWW1rtgHHKwp3HQd7qC",  -- Password: "123"
    "John", "Doe", "1981-06-08", "China Eastern"
);
INSERT INTO Airline_Staff VALUES (
    "emily.johnson@americanair.com", 
    "$2b$12$QH7HxpFhSs1G7m5/s7tHK.nsTsztKZj8MjDWW1rtgHHKwp3HQd7qC",  -- Password: "123"
    "Emily", "Johnson", "1990-03-15", "American Airlines"
);

-- Insert flights (more realistic flight numbers & schedules)
INSERT INTO Flight VALUES (
    "China Eastern", "588", "JFK", "2025-01-01 08:00:00", "PVG", "2025-01-02 12:00:00",
    "1200", "in_progress", "1"
);
INSERT INTO Flight VALUES (
    "China Eastern", "589", "PVG", "2025-01-15 10:00:00", "JFK", "2025-01-15 14:00:00",
    "1200", "upcoming", "2"
);
INSERT INTO Flight VALUES (
    "Japan Airlines", "188", "HND", "2025-02-01 09:00:00", "JFK", "2025-02-01 14:00:00",
    "1500", "delayed", "3"
);
INSERT INTO Flight VALUES (
    "American Airlines", "300", "JFK", "2025-03-01 07:00:00", "LAX", "2025-03-01 10:00:00",
    "400", "delayed", "4"
);
INSERT INTO Flight VALUES (
    "Emirates", "202", "DXB", "2025-04-01 22:00:00", "JFK", "2025-04-02 06:00:00",
    "1800", "on-time", "5"
);

-- Insert tickets (sequential IDs)
INSERT INTO Ticket VALUES ("1001", "China Eastern", "588");
INSERT INTO Ticket VALUES ("1002", "China Eastern", "588");
INSERT INTO Ticket VALUES ("1003", "China Eastern", "589");
INSERT INTO Ticket VALUES ("2001", "Japan Airlines", "188");
INSERT INTO Ticket VALUES ("3001", "American Airlines", "300");
INSERT INTO Ticket VALUES ("4001", "Emirates", "202");

-- Insert purchases (realistic purchase dates)
INSERT INTO purchases VALUES ("1001", "alice.wang@email.com", NULL, "2024-12-01");
INSERT INTO purchases VALUES ("1002", "bob.li@email.com", "10001", "2024-12-05");
INSERT INTO purchases VALUES ("2001", "john.doe@email.com", "10002", "2025-01-10");
INSERT INTO purchases VALUES ("3001", "sarah.smith@email.com", NULL, "2025-02-15");
INSERT INTO purchases VALUES ("4001", "alice.wang@email.com", "10003", "2025-03-20");

-- Insert booking agent work relationships
INSERT INTO booking_agent_work_for VALUES ("travel.agent1@agency.com", "China Eastern");
INSERT INTO booking_agent_work_for VALUES ("travel.agent1@agency.com", "Japan Airlines");
INSERT INTO booking_agent_work_for VALUES ("travel.agent2@agency.com", "American Airlines");
INSERT INTO booking_agent_work_for VALUES ("global.travel@agency.com", "Emirates");

-- Insert permissions
INSERT INTO permission VALUES ("jack.goodman@chinaeastern.com", "Admin");
INSERT INTO permission VALUES ("john.doe@chinaeastern.com", "Operator");
INSERT INTO permission VALUES ("emily.johnson@americanair.com", "Admin");