<exercise>
  <div if={loading} class="valign-wrapper" style="width: 100%; height: 100%">
    <spinner size="big" class="center-align" style="margin: auto"></spinner>
  </div>

  <div class="row" if={!loading && !completed}>
    <div class="col s8 center-align offset-s2">
      <a each={w in words} class="waves-effect waves-light btn" data-word={w} onclick={chooseWord}>{w.replace("_"," ")}</a>
      <a class="orange lighten-2 waves-effect waves-light btn" data-word="=SKIP=" onclick={chooseWord}>I'm not sure</a>
      <a class="red lighten-2 waves-effect waves-light btn" href="#">Quit</a>
    </div>
  </div>

  <div class="row" if={!loading && completed}>
    <div class="col s12">
      <div class="card">
        <div class="card-content">
          <span class="card-title">You have completed the exercise</span>
          <p>Congratulations! You have successfully completed the whole exercise. This is how you match the gold standard:</p>
          <div style="width: 40%; margin-top: 2em; margin-bottom: 2em" id="evaluation"></div>
          <p>But as you know, even the gold standard may be wrong...</p>
        </div>
        <div class="card-action">
          <a href="#">Return to main page</a>
        </div>
      </div>
    </div>
  </div>
  <style>
    a {
      margin: .5em;
      display: inline-block;
    }
  </style>
 
  <script>
    this.words = []
    this.completed = false
    this.loading = false
    this.evaluating = false

    chooseWord(e) {
      this.loading = true
      this.update()
      $.get("exercise.cgi?action=next&id=" + this.parent.exercise_id + "&chosen=" + encodeURIComponent(e.currentTarget.dataset.word), (data) => {
        this.words = data.words;
        this.completed = data.completed;
        this.loading = false
        this.update()
      })
    }
    this.on("mount", () => {
      this.loading = true
      this.update()
      $.get("exercise.cgi?action=next&id=" + this.parent.exercise_id, (data) => {
        this.words = data.words;
        this.completed = data.completed;
        this.loading = false
        this.update()
      })
    })
    this.on("updated", () => {
      if (this.completed) {
        if (!this.bar) {
          this.evaluating = true;
          this.bar = new ProgressBar.SemiCircle(document.getElementById("evaluation"), {
            strokeWidth: 6,
            color: '#FFEA82',
            trailColor: '#eee',
            trailWidth: 1,
            easing: 'easeInOut',
            duration: 1400,
            svgStyle: null,
            text: {
              value: '',
              alignToBottom: false
            },
            from: {color: '#FFEA82'},
            to: {color: '#48ff45'},
            // Set default step function for all animate calls
            step: (state, bar) => {
              bar.path.setAttribute('stroke', state.color);
              if (this.evaluating)
                bar.setText("evaluating...")
              else
                bar.setText((bar.value() * 100).toFixed(2) + " %");
              bar.text.style.color = state.color;
              bar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
              bar.text.style.fontSize = '2rem';
            }
          });
          this.bar.animate(0);  // Number from 0.0 to 1.0
          $.get("exercise.cgi?action=eval&id=" + this.parent.exercise_id, (data) => {
            this.evaluating = false
            this.bar.animate((data[0]["correct"]/data[0]["total"]).toFixed(2))
          })
        }
      }
    })
  </script>

</exercise>
