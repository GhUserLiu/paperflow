## 📚 Paper Collection Log - 2026-01-05 04:15:56 UTC

### Execution Details
- **Trigger**: Scheduled (Daily at 3:00 AM UTC)
- **Workflow Run**: [#17](https://github.com/GhUserLiu/arxiv-zotero-auto/actions/runs/20704888857)

### Recent Logs (Last 50 lines)
```
2026-01-05 04:15:34,495 - INFO - HTTP Request: GET https://api.zotero.org/users/19092277/collections?format=json&limit=100&locale=en-US "HTTP/1.1 200 OK"
2026-01-05 04:15:34,495 - INFO - Successfully validated collection LRML5CDJ
2026-01-05 04:15:34,496 - INFO - Executing arXiv search with query: (("intelligent connected vehicles" OR "autonomous driving") AND (communication OR perception OR "sensor fusion" OR planning) NOT survey NOT review)
2026-01-05 04:15:34,496 - INFO - Requesting page (first: True, try: 0): https://export.arxiv.org/api/query?search_query=%28%28%22intelligent+connected+vehicles%22+OR+%22autonomous+driving%22%29+AND+%28communication+OR+perception+OR+%22sensor+fusion%22+OR+planning%29+NOT+survey+NOT+review%29&id_list=&sortBy=submittedDate&sortOrder=descending&start=0&max_results=100
2026-01-05 04:15:36,198 - INFO - Got first page: 100 of 3084 total results
2026-01-05 04:15:36,198 - ERROR - Error searching arXiv: can't compare offset-naive and offset-aware datetimes
2026-01-05 04:15:36,198 - INFO - Found 0 papers matching the criteria
2026-01-05 04:15:39,515 - INFO - HTTP Request: GET https://api.zotero.org/users/19092277/collections?format=json&limit=100&locale=en-US "HTTP/1.1 200 OK"
2026-01-05 04:15:39,516 - INFO - Successfully validated collection 3E4NFDPR
2026-01-05 04:15:39,516 - INFO - Executing arXiv search with query: (("V2X" OR "vehicle-to-everything" OR VANET) AND (security OR "semantic communication" OR latency OR "beamforming") NOT survey NOT review)
2026-01-05 04:15:39,517 - INFO - Requesting page (first: True, try: 0): https://export.arxiv.org/api/query?search_query=%28%28%22V2X%22+OR+%22vehicle-to-everything%22+OR+VANET%29+AND+%28security+OR+%22semantic+communication%22+OR+latency+OR+%22beamforming%22%29+NOT+survey+NOT+review%29&id_list=&sortBy=submittedDate&sortOrder=descending&start=0&max_results=100
2026-01-05 04:15:41,162 - INFO - Got first page: 100 of 374 total results
2026-01-05 04:15:41,162 - ERROR - Error searching arXiv: can't compare offset-naive and offset-aware datetimes
2026-01-05 04:15:41,163 - INFO - Found 0 papers matching the criteria
2026-01-05 04:15:44,264 - INFO - HTTP Request: GET https://api.zotero.org/users/19092277/collections?format=json&limit=100&locale=en-US "HTTP/1.1 200 OK"
2026-01-05 04:15:44,264 - INFO - Successfully validated collection 8CQV3SDV
2026-01-05 04:15:44,265 - INFO - Executing arXiv search with query: ((camera OR lidar OR radar OR "sensor fusion") AND ("autonomous driving" OR "object detection" OR "trajectory prediction") NOT survey NOT review)
2026-01-05 04:15:44,265 - INFO - Requesting page (first: True, try: 0): https://export.arxiv.org/api/query?search_query=%28%28camera+OR+lidar+OR+radar+OR+%22sensor+fusion%22%29+AND+%28%22autonomous+driving%22+OR+%22object+detection%22+OR+%22trajectory+prediction%22%29+NOT+survey+NOT+review%29&id_list=&sortBy=submittedDate&sortOrder=descending&start=0&max_results=100
2026-01-05 04:15:46,887 - INFO - Got first page: 100 of 3968 total results
2026-01-05 04:15:46,888 - ERROR - Error searching arXiv: can't compare offset-naive and offset-aware datetimes
2026-01-05 04:15:46,888 - INFO - Found 0 papers matching the criteria
2026-01-05 04:15:49,975 - INFO - HTTP Request: GET https://api.zotero.org/users/19092277/collections?format=json&limit=100&locale=en-US "HTTP/1.1 200 OK"
2026-01-05 04:15:49,976 - INFO - Successfully validated collection 8862N8CE
2026-01-05 04:15:49,976 - INFO - Executing arXiv search with query: (("path planning" OR "motion planning" OR "model predictive ""control" OR MPC) AND vehicle NOT survey NOT review)
2026-01-05 04:15:49,977 - INFO - Requesting page (first: True, try: 0): https://export.arxiv.org/api/query?search_query=%28%28%22path+planning%22+OR+%22motion+planning%22+OR+%22model+predictive+%22%22control%22+OR+MPC%29+AND+vehicle+NOT+survey+NOT+review%29&id_list=&sortBy=submittedDate&sortOrder=descending&start=0&max_results=100
2026-01-05 04:15:51,790 - INFO - Got first page: 100 of 11394 total results
2026-01-05 04:15:51,791 - ERROR - Error searching arXiv: can't compare offset-naive and offset-aware datetimes
2026-01-05 04:15:51,791 - INFO - Found 0 papers matching the criteria
2026-01-05 04:15:55,004 - INFO - HTTP Request: GET https://api.zotero.org/users/19092277/collections?format=json&limit=100&locale=en-US "HTTP/1.1 200 OK"
2026-01-05 04:15:55,005 - INFO - Successfully validated collection S97HI5KX
2026-01-05 04:15:55,005 - INFO - Executing arXiv search with query: ((safety OR security OR privacy OR "adversarial attack") AND ("autonomous vehicle" OR "connected vehicle") NOT survey NOT review)
2026-01-05 04:15:55,005 - INFO - Requesting page (first: True, try: 0): https://export.arxiv.org/api/query?search_query=%28%28safety+OR+security+OR+privacy+OR+%22adversarial+attack%22%29+AND+%28%22autonomous+vehicle%22+OR+%22connected+vehicle%22%29+NOT+survey+NOT+review%29&id_list=&sortBy=submittedDate&sortOrder=descending&start=0&max_results=100
2026-01-05 04:15:56,858 - INFO - Got first page: 100 of 2005 total results
2026-01-05 04:15:56,858 - ERROR - Error searching arXiv: can't compare offset-naive and offset-aware datetimes
2026-01-05 04:15:56,859 - INFO - Found 0 papers matching the criteria
```
