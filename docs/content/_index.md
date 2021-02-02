---
title: "DefectDojo\'s Documentation"
date: 2021-02-02T20:46:29+01:00
draft: false
---

DefectDojo\'s Documentation
===========================

![image](../images/dashboard.png)

**About DefectDojo**

*What is DefectDojo?*

![image](../images/bug-2x.png)

[DefectDojo]{.title-ref} is a security tool that automates application
security vulnerability management. [DefectDojo]{.title-ref} streamlines
the application security testing process by offering features such as
importing third party security findings, merging and de-duping,
integration with Jira, templating, report generation and security
metrics.

*What does DefectDojo do?*

![image](../images/graph-2x.png)

While traceability and metrics are the ultimate end goal, DefectDojo is
a bug tracker at its core. Taking advantage of DefectDojo\'s
Product:Engagement model, enables traceability among multiple projects
and test cycles, and allows for fine-grained reporting.

*How does DefectDojo work?*

![image](../images/key-2x.png)

DefectDojo is based on a model that allows the ultimate flexibility in
your test tracking needs.

-   Working in DefectDojo starts with a `Product Type`.
-   Each Product Type can have one or more `Products`.
-   Each Product can have one or more `Engagements`.
-   Each Engagement can have one or more `Tests`.
-   Each Test can have one or more `Findings`.

![image](../images/DD-Hierarchy.png)

The code is open source, and [available on
github](https://github.com/DefectDojo/django-DefectDojo) and a running
example is available on [the demo server](https://demo.defectdojo.org)
using the credentials `admin / defectdojo@demo#appsec`. Note: The demo
server is refreshed regularly and provisioned some sample data.

Our documentation is organized in the following sections:

-   `user-docs`{.interpreted-text role="ref"}
-   `feature-docs`{.interpreted-text role="ref"}
-   `api-docs`{.interpreted-text role="ref"}
-   `plugin-docs`{.interpreted-text role="ref"}
-   `dev-docs`{.interpreted-text role="ref"}

User Documentation {#user-docs}
------------------

::: {.toctree maxdepth="2"}
about getting-started integrations models start-using workflows
upgrading running-in-production
:::

Feature Documentation {#feature-docs}
---------------------

::: {.toctree maxdepth="2" glob=""}
features social-authentication
:::

API and settings Documentation {#api-docs}
------------------------------

::: {.toctree maxdepth="2" glob=""}
api-docs api-v2-docs settings-docs
:::

Plugins {#plugin-docs}
-------

::: {.toctree maxdepth="2" glob=""}
burp-plugin
:::

Dev Documentation {#dev-docs}
-----------------

::: {.toctree maxdepth="2" glob=""}
how-to-write-a-parser
:::
