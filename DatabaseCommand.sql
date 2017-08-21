Create extension pgcrypto;

CREATE TABLE public.users_type
(
  id integer NOT NULL nextval('users_type_id_seq'::regclass),
  type character varying,
  CONSTRAINT users_type_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.users_type
  OWNER TO postgres;


CREATE TABLE public.users
(
  id bigint NOT NULL DEFAULT nextval('users_id_seq'::regclass),
  first_name character varying,
  last_name character varying,
  email character varying,
  phone_number integer,
  password character varying,
  user_type_id integer,
  CONSTRAINT users_pkey PRIMARY KEY (id),
  CONSTRAINT users_user_type_id_fkey FOREIGN KEY (user_type_id)
      REFERENCES public.users_type (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.users
  OWNER TO postgres;


CREATE TABLE public.category
(
  id integer NOT NULL DEFAULT nextval('category_id_seq'::regclass),
  title character varying,
  CONSTRAINT category_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.category
  OWNER TO postgres;


CREATE TABLE public.deliveries_type
(
  id integer NOT NULL DEFAULT nextval('deliveries_type_id_seq'::regclass),
  title character varying,
  price numeric(10,2),
  CONSTRAINT deliveries_type_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.deliveries_type
  OWNER TO postgres;


CREATE TABLE public.products
(
  id bigint NOT NULL DEFAULT nextval('products_id_seq'::regclass),
  image bytea,
  title character varying,
  description character varying,
  product_value numeric(15,2),
  curency_unit character varying,
  comments character varying,
  likes integer,
  category_id integer NOT NULL,
  CONSTRAINT products_pkey PRIMARY KEY (id),
  CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id)
      REFERENCES public.category (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.products
  OWNER TO postgres;


CREATE TABLE public.order_details
(
  id bigint NOT NULL nextval('order_details_id_seq'::regclass),
  order_id integer,
  product_id integer,
  product_counts integer,
  CONSTRAINT order_details_pkey PRIMARY KEY (id),
  CONSTRAINT order_details_order_id_fkey FOREIGN KEY (order_id)
      REFERENCES public.orders (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT order_details_product_id_fkey FOREIGN KEY (product_id)
      REFERENCES public.products (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.order_details
  OWNER TO postgres;

CREATE TABLE public.orders
(
  id bigint NOT NULL DEFAULT nextval('orders_id_seq'::regclass),
  user_id bigint,
  delivery_type_id integer,
  description character varying,
  total_price numeric(15,2),
  product_counts_sum integer,
  staff_id integer,
  shop_id integer,
  create_time timestamp without time zone DEFAULT now(),
  CONSTRAINT orders_pkey PRIMARY KEY (id),
  CONSTRAINT orders_delivery_type_id_fkey FOREIGN KEY (delivery_type_id)
      REFERENCES public.deliveries_type (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES public.users (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.orders
  OWNER TO postgres;


