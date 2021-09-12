-- name: create_schema#
create table if not exists repos (
    id integer not null primary key,
    name text not null,
    path text not null,
    cache_logs integer default 0
);

create table if not exists logs (
    id integer not null primary key,
    repo_id integer not null,
    revision integer not null,
    log_entry blob not null,
    foreign key(repo_id) references repos(id),
    unique(repo_id, revision)
);

create table if not exists notes (
    id integer not null primary key,
    repo_id integer not null,
    changelist_name text,
    path_name text,
    foreign key(repo_id) references repos(id)
);