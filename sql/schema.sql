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
    revision text not null,
    message blob not null,
    paths blob not null,
    foreign key(repo_id) references repos(id)
);
