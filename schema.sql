--
-- PostgreSQL database dump
--

-- Dumped from database version 15.3
-- Dumped by pg_dump version 15.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: results; Type: TABLE; Schema: public; Owner: helmer
--

CREATE TABLE public.results (
    id integer NOT NULL,
    user_id integer,
    movement_id integer,
    weight integer,
    date date
);


ALTER TABLE public.results OWNER TO helmer;

--
-- Name: results_id_seq; Type: SEQUENCE; Schema: public; Owner: helmer
--

CREATE SEQUENCE public.results_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.results_id_seq OWNER TO helmer;

--
-- Name: results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: helmer
--

ALTER SEQUENCE public.results_id_seq OWNED BY public.results.id;


--
-- Name: results id; Type: DEFAULT; Schema: public; Owner: helmer
--

ALTER TABLE ONLY public.results ALTER COLUMN id SET DEFAULT nextval('public.results_id_seq'::regclass);


--
-- Name: results results_pkey; Type: CONSTRAINT; Schema: public; Owner: helmer
--

ALTER TABLE ONLY public.results
    ADD CONSTRAINT results_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

