drop table if exists entries;

create table entries (
  isbn string primary key,
  title string not null,
  author string not null,
  description string not null
);
