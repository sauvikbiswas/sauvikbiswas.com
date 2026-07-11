---
title: "OAuth2: one step at a time"
categories:
  - "static"
hidePagination: true
---

Companion posts for [oauth-lab on GitHub](https://github.com/sauvikbiswas/oauth-lab): incremental Flask snapshots from authorization code flow through JWKS, RS256, RFC 8707 resource indicators, and RFC 8693 token exchange (on-behalf-of). Read in order.

1. v01 – _[Learning OAuth 2 by Building It, One Version at a Time]({{< relref "posts/learning-oauth-2-01" >}})_
2. v02 – _[Adding OAuth State to Stop CSRF]({{< relref "posts/learning-oauth-2-02" >}})_
3. v03 – _[Adding PKCE to Stop Authorization Code Interception]({{< relref "posts/learning-oauth-2-03" >}})_
4. v04 – _[Using the Access Token on a Protected API]({{< relref "posts/learning-oauth-2-04" >}})_
5. v05 – _[Refresh Tokens and Silent Re-authentication]({{< relref "posts/learning-oauth-2-05" >}})_
6. v06 – _[Splitting the Auth Server from the Resource Server]({{< relref "posts/learning-oauth-2-06" >}})_
7. v06b – _[JWT Access Tokens: Local Validation Without the Introspection Hop]({{< relref "posts/learning-oauth-2-06b" >}})_
8. v07 – _[Adding OpenID Connect on Top of OAuth 2]({{< relref "posts/learning-oauth-2-07" >}})_
9. Intermission – _[What Industry Ships and Who Gets Paid]({{< relref "posts/learning-oauth-2-intermission-01" >}})_
10. v08 – _[JWKS and RS256: Dropping the Shared JWT Secret]({{< relref "posts/learning-oauth-2-08" >}})_
11. v09 – _[Resource Indicators: Binding Tokens to a Specific API]({{< relref "posts/learning-oauth-2-09" >}})_
12. v10 – _[Token Exchange (On-Behalf-Of): Swapping Tokens for Downstream APIs]({{< relref "posts/learning-oauth-2-10" >}})_

## A note on usage of LLMs

These posts and the [oauth-lab](https://github.com/sauvikbiswas/oauth-lab) repo were written while I was learning OAuth and OIDC myself. I used LLMs heavily: boilerplate and styling in the Flask apps, RFC lookups, diagram and table formatting, prose cleanup, and (in the intermission post) market research and reference gathering.

The protocol flow, security tradeoffs, and what each version adds are things I built and debugged by hand. When something in a post reads too polished or too generic, that is probably the model; when it describes a bug I hit or a `/debug/state` dump that looked wrong, that is me.

Treat vendor numbers and analyst figures as snapshots, not gospel. Verify anything you plan to rely on against primary sources. If you spot an error, [open an issue](https://github.com/sauvikbiswas/oauth-lab/issues) or tell me.

## History of changes

*2026.07.11:* Split JWT local validation out of v06 into a companion post ([v06b]({{< relref "posts/learning-oauth-2-06b" >}})). v06 was doing too much at once: server split plus both introspection and JWT Mode B; and those JWT claims resurface properly in v08 with JWKS anyway. Also added a few forward links now that later posts are live.