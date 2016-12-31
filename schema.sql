drop table if exists entries;
drop table if exists flow;
create table entries (
  isbn string primary key,
  title string not null,
  author string not null,
  description string not null
);

create table flow (
  isbn1 string,
  isbn2 string,
  cnt integer,
  foreign key(isbn1) references entries(isbn),
  foreign key(isbn2) references entries(isbn)
)