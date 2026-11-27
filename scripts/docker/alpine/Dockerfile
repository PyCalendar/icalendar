FROM python:3.14.10-alpine3.24

WORKDIR /tmp

# Apply Alpine and pip security updates; only upgrade setuptools if present.
RUN apk upgrade --no-cache \
    && python -m pip install --no-cache-dir --upgrade pip \
    && if python -m pip show setuptools >/dev/null 2>&1; then \
        python -m pip install --no-cache-dir --upgrade 'setuptools>=78.1.1'; \
    fi

# Install pinned test dependencies.
RUN python -m pip install --no-cache-dir \
    pytest==9.2.0 \
    hypothesis==6.170.17 \
    pytz==2026.6

COPY dist/ /tmp/dist/

RUN python -m pip install --no-cache-dir /tmp/dist/icalendar-*.tar.gz \
    && mkdir -p /tmp/icalendar-src \
    && tar -xzf /tmp/dist/icalendar-*.tar.gz \
        -C /tmp/icalendar-src --strip-components=1

WORKDIR /tmp/icalendar-src

CMD ["python", "-c", "import pathlib, sysconfig, icalendar, pytest; package = pathlib.Path(icalendar.__file__).resolve(); site_packages = pathlib.Path(sysconfig.get_paths()['purelib']).resolve(); assert package.is_relative_to(site_packages), package; print(package); raise SystemExit(pytest.main(['--import-mode=importlib', 'src/icalendar/tests']))"]
