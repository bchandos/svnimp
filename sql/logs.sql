-- name: cache_log
-- cache an individual log, as JSON representing the dictionary
insert into logs(repo_id, revision, log_entry) 
values (:repo_id, :revision, :log_entry);

-- name: get_logs
-- retrieve cached logs between two revision numbers
select log_entry from logs
where repo_id = :repo_id 
and revision between :start_rev AND :end_rev;

-- name: get_log
-- retrieve changed log entry for specific revision
select log_entry from logs
where repo_id = :repo_id
and revision = :start_rev;
