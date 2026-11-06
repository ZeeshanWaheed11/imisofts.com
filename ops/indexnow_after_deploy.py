"""Submit queued URLs to IndexNow only after the deploy is live (proposed 2026-11-06).

Until now each build script pinged IndexNow inside the build step, before the bot commit
was pushed and before Cloudflare Pages deployed it, so Bing could fetch a page that did not
exist yet. With INDEXNOW_QUEUE set, the builds write their URL list to that file instead,
and this step (run after `git push`) waits for the deploy, checks that every queued URL
answers 200 on the live site, then submits only the live ones. It never fails the workflow.
"""
import json, os, sys, time, urllib.request

KEY = "8f91c62405dc13875a9db237c23b51f6"
QUEUE = os.environ.get("INDEXNOW_QUEUE", "/tmp/indexnow_queue.json")
FIRST_WAIT = int(os.environ.get("INDEXNOW_FIRST_WAIT", "150"))  # seconds for Cloudflare Pages to deploy
MAX_WAIT = int(os.environ.get("INDEXNOW_MAX_WAIT", "900"))      # give up on a URL after this


def is_live(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "imisofts-indexnow-check"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return getattr(r, "status", r.getcode()) == 200
    except Exception:
        return False


def main():
    if not os.path.exists(QUEUE):
        print("indexnow: no queue file, nothing to submit")
        return 0
    urls = list(dict.fromkeys(json.load(open(QUEUE))))
    if not urls:
        print("indexnow: queue empty")
        return 0
    print("indexnow: waiting %ds for the deploy, then checking %d url(s)" % (FIRST_WAIT, len(urls)))
    time.sleep(FIRST_WAIT)
    pending, live = set(urls), []
    deadline = time.time() + MAX_WAIT
    while pending and time.time() < deadline:
        for u in sorted(pending):
            if is_live(u):
                live.append(u)
                pending.discard(u)
        if pending:
            time.sleep(30)
    if pending:
        print("indexnow: not live after the wait, NOT submitted: %s" % sorted(pending))
    if not live:
        return 0
    payload = json.dumps({"host": "imisofts.com", "key": KEY,
                          "keyLocation": f"https://imisofts.com/{KEY}.txt", "urlList": live}).encode()
    try:
        req = urllib.request.Request("https://api.indexnow.org/indexnow", data=payload,
                                     headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
        with urllib.request.urlopen(req, timeout=20) as r:
            print("indexnow: submitted %d live url(s), HTTP %s" % (len(live), getattr(r, "status", r.getcode())))
    except Exception as e:
        print("indexnow: skipped (%s)" % e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
