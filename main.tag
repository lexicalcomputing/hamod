<main>
  <div class="container">
    <div data-is={content} ref="content"></div>
  </div>

  <script>
    this.content = "new"
    this.name = ""
    this.userid = ""

    onEditRecord(num, type) {
      route("edit/" + type + "/" + num)
    }

    onShowOverview(e) {
      route("overview/" + this.type)
    }

    this.on("mount", () => {
      /* ROUTING */
      route('/exercise/*', (ex_id) => {
        this.content = "exercise"
        this.exercise_id = decodeURIComponent(ex_id)
        this.update()
      })
      route('/new', (type) => {
        this.content = "new"
        this.update()
      })
      route('/', () => {
        this.content = "new"
        this.update()
      })
      route.start (true)

    })
  </script>

  <style>
    h3 { color: #444 }
    ul { color: #999 }
  </style>
</main>


<!-- vim: set ts=2 sw=2 :-->
