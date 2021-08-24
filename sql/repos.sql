-- name: get_all_repos
-- Get all repositories
select id, name, path
from repos;

-- name: get_repo_by_id^
-- Get repo by id
select id, name, path
from repos
where id = :id;

-- name: create_repo!
-- Create a new repo
insert into repos(name, path, cache_logs) values (:name, :path, :cache_logs);

-- name: update_repo_cache_logs!
-- Update the value of the cache_logs column
update repos set cache_logs = :cache_logs where id = :id;