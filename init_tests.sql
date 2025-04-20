USE test_db;



DECLARE @test_status_codes_100 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Tests VALUES (@test_status_codes_100, '1xx Status Codes', 'Test about informational responses');

DECLARE @test_sc_100_q1 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_100_q1, @test_status_codes_100, 'Name of the 100 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_100_q1, 'Continue', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_100_q1, 'Proceed', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_100_q1, 'Start', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_100_q1, 'Begin', 0);

DECLARE @test_sc_100_q2 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_100_q2, @test_status_codes_100, 'Name of the 101 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_100_q2, 'Switching Protocols', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_100_q2, 'Switching Platforms', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_100_q2, 'Switching Browsers', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_100_q2, 'Switching Sites', 0);

DECLARE @test_sc_100_q3 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_100_q3, @test_status_codes_100, 'Name of the 102 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_100_q3, 'Processing', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_100_q3, 'Thinking', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_100_q3, 'Server Error', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_100_q3, 'Client Error', 0);

DECLARE @test_sc_100_q4 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_100_q4, @test_status_codes_100, 'Name of the 103 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_100_q4, 'Early Hints', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_100_q4, 'Too Early', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_100_q4, 'Late Hints', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_100_q4, 'Too Late', 0);



DECLARE @test_status_codes_200 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Tests VALUES (@test_status_codes_200, '2xx Status Codes', 'Test about successful responses');

DECLARE @test_sc_200_q1 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_200_q1, @test_status_codes_200, 'Name of the 200 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_200_q1, 'OK', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_200_q1, 'Success', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_200_q1, 'Accepted', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_200_q1, 'Completed', 0);

DECLARE @test_sc_200_q2 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_200_q2, @test_status_codes_200, 'Name of the 201 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_200_q2, 'Created', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_200_q2, 'Generated', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_200_q2, 'Built', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_200_q2, 'Saved', 0);

DECLARE @test_sc_200_q3 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_200_q3, @test_status_codes_200, 'Name of the 202 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_200_q3, 'Accepted', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_200_q3, 'Created', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_200_q3, 'OK', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_200_q3, 'Success', 0);

DECLARE @test_sc_200_q4 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_200_q4, @test_status_codes_200, 'Name of the 204 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_200_q4, 'No Content', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_200_q4, 'Success', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_200_q4, 'OK', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_200_q4, 'Created', 0);



DECLARE @test_status_codes_300 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Tests VALUES (@test_status_codes_300, '3xx Status Codes', 'Test about redirection responses');

DECLARE @test_sc_300_q1 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_300_q1, @test_status_codes_300, 'Name of the 301 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_300_q1, 'Moved Permanently', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_300_q1, 'Found', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_300_q1, 'Redirected', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_300_q1, 'Moved Temporarily', 0);

DECLARE @test_sc_300_q2 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_300_q2, @test_status_codes_300, 'Name of the 302 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_300_q2, 'Found', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_300_q2, 'Temporary Redirect', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_300_q2, 'Moved Permanently', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_300_q2, 'See Other', 0);

DECLARE @test_sc_300_q3 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_300_q3, @test_status_codes_300, 'Name of the 303 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_300_q3, 'See Other', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_300_q3, 'Redirected', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_300_q3, 'Moved Temporarily', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_300_q3, 'Moved Permanently', 0);

DECLARE @test_sc_300_q4 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_300_q4, @test_status_codes_300, 'Name of the 307 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_300_q4, 'Temporary Redirect', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_300_q4, 'Found', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_300_q4, 'Moved Permanently', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_300_q4, 'See Other', 0);



DECLARE @test_status_codes_400 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Tests VALUES (@test_status_codes_400, '4xx Status Codes', 'Test about client error responses');

DECLARE @test_sc_400_q1 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_400_q1, @test_status_codes_400, 'Name of the 400 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_400_q1, 'Bad Request', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_400_q1, 'Not Found', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_400_q1, 'Unauthorized', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_400_q1, 'Forbidden', 0);

DECLARE @test_sc_400_q2 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_400_q2, @test_status_codes_400, 'Name of the 404 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_400_q2, 'Not Found', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_400_q2, 'Missing', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_400_q2, 'Unavailable', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_400_q2, 'Bad Gateway', 0);

DECLARE @test_sc_400_q3 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_400_q3, @test_status_codes_400, 'Name of the 401 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_400_q3, 'Unauthorized', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_400_q3, 'Forbidden', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_400_q3, 'Not Found', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_400_q3, 'Bad Request', 0);

DECLARE @test_sc_400_q4 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_400_q4, @test_status_codes_400, 'Name of the 408 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_400_q4, 'Request Timeout', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_400_q4, 'Gateway Timeout', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_400_q4, 'Bad Request', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_400_q4, 'Not Found', 0);



DECLARE @test_status_codes_500 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Tests VALUES (@test_status_codes_500, '5xx Status Codes', 'Test about server error responses');

DECLARE @test_sc_500_q1 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_500_q1, @test_status_codes_500, 'Name of the 500 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_500_q1, 'Internal Server Error', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_500_q1, 'Server Busy', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_500_q1, 'Bad Gateway', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_500_q1, 'Unavailable', 0);

DECLARE @test_sc_500_q2 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_500_q2, @test_status_codes_500, 'Name of the 502 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_500_q2, 'Bad Gateway', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_500_q2, 'Gateway Timeout', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_500_q2, 'Internal Server Error', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_500_q2, 'Service Unavailable', 0);

DECLARE @test_sc_500_q3 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_500_q3, @test_status_codes_500, 'Name of the 503 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_500_q3, 'Service Unavailable', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_500_q3, 'Internal Server Error', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_500_q3, 'Bad Gateway', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_500_q3, 'Gateway Timeout', 0);

DECLARE @test_sc_500_q4 UNIQUEIDENTIFIER = NEWID();
INSERT INTO Questions VALUES (@test_sc_500_q4, @test_status_codes_500, 'Name of the 504 status code:');
INSERT INTO Answers VALUES (NEWID(), @test_sc_500_q4, 'Gateway Timeout', 1);
INSERT INTO Answers VALUES (NEWID(), @test_sc_500_q4, 'Service Unavailable', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_500_q4, 'Bad Gateway', 0);
INSERT INTO Answers VALUES (NEWID(), @test_sc_500_q4, 'Internal Server Error', 0);