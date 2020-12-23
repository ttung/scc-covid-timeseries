#!/usr/bin/env bash

dir="${1:?A path to the raw-datasets directory must be provided as the first argument.}"

now=$(date +%Y%m%d-%H%M)

function fetch() {
    curl --retry 5 -o "${dir}"/"${SUBDIR}"/"${now}".csv -D "${dir}"/"${SUBDIR}"/"${now}".headers "https://data.sccgov.org/resource/${IDENTIFIER}.csv"
}

SUBDIR=cases-by-city			IDENTIFIER=59wk-iusg	fetch
SUBDIR=cases-by-zip			IDENTIFIER=j2gj-bg6c	fetch
SUBDIR=deaths-by-age-group		IDENTIFIER=pg8z-gbgv	fetch
SUBDIR=deaths-by-race-ethnicity		IDENTIFIER=nd69-4zii	fetch
SUBDIR=cases-by-transmission-method	IDENTIFIER=xar3-th86	fetch
SUBDIR=deaths-by-comorbidity		IDENTIFIER=mejj-pzbm	fetch
SUBDIR=cases-by-age-group		IDENTIFIER=ige8-ixqu	fetch
SUBDIR=tests-by-popup			IDENTIFIER=5hkv-ampu	fetch
SUBDIR=deaths-by-gender			IDENTIFIER=v49w-v4a7	fetch
SUBDIR=cases-by-ltcf			IDENTIFIER=xtg3-85g6	fetch
SUBDIR=cases-by-ethnicity		IDENTIFIER=ccm2-45w3	fetch
SUBDIR=tests-by-healthcare-system	IDENTIFIER=vzxr-ymut	fetch
SUBDIR=cases-by-gender			IDENTIFIER=ibdk-7rf5	fetch
SUBDIR=ltcf				IDENTIFIER=kb5s-tppg	fetch
