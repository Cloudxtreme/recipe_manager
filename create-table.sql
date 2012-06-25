create table recipes
(
  name varchar(96) not null,
  ingredients text,
  directions text,
  notes text,
  id int unsigned auto_increment not null primary key,
  original_source smallint unsigned default 1,
  food_type smallint unsigned not null default 1,
  rating tinyint unsigned not null default 5
);

create table original_source
(
  id smallint unsigned auto_increment not null primary key,
  name char(128)
);

create table food_type
(
  id tinyint unsigned auto_increment not null primary key,
  name char(128)
);

insert into original_source values(1,"Unknown");
insert into food_type values(1,"Entree");
insert into food_type values(2,"Desert");
insert into food_type values(3,"Beverage");