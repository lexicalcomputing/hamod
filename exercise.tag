<exercise>
  <div if={loading} class="valign-wrapper" style="width: 100%; height: 100%">
    <spinner size="big" class="center-align" style="margin: auto"></spinner>
  </div>

  <div class="row" if={!completed}>
    <div>
      <div id="progress"></div>
    </div>
  </div>

  <div class="row" if={!loading && !completed}>
    <div class="col s8 center-align offset-s2">
      <div if={showprev}>Clicked too fast? <a href="javascript:void(0)" onclick={undoLast}>Undo last click!</a></div>
      <div if={waittime > 0}>Please read and think about the outlier word. Buttons become active in {waittime} seconds.</div>
      <div if={waittime <= 0}>Please click the outlier word.</div>
      <a each={w in words} class="waves-effect waves-light btn disabled" data-word={w} onclick={chooseWord}>{w.replaceAll("_"," ")}</a>
      <br/>
      <a if={waittime <= 0} class="orange lighten-2 waves-effect waves-light btn" data-word="=SKIP=" onclick={chooseWord}>I'm not sure</a>
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
    a.btn{
      font-weight: bold;
    }
    a.btn.disabled {
      color: black !important;
    }
    #progress {
      margin: auto;
      margin-bottom: 20px;
      width: 40%;
      height: 8px;
      position: relative;
    }
  </style>
 
  <script>
    this.words = []
    this.completed = false
    this.loading = true
    this.evaluating = false
    this.progress = 0.0
    this.todo = 0
    this.waittime = 5
    this.showprev = (this.progress > 0);

    stepInterval() {
      this.waittime--;
      if (!this.waittime) {
        clearInterval(this.timer);
        $(".btn.disabled").removeClass("disabled")
      }
      this.update()
    }

    chooseWord(e) {
      this.loadData({action: "next", chosen: e.currentTarget.dataset.word})
      this.showprev = true
    }

    undoLast() {
      this.loadData({action: "undo"})
      this.showprev = false
    }

    this.on("mount", () => {
      this.loadData({action: "next"})
    })

    loadData(params) {
      params["id"] = this.parent.exercise_id;
      this.loading = true
      this.update()
      $.get("exercise.cgi", params, (data) => {
        this.words = data.words;
        this.completed = data.completed;
        this.progress = data.progress;
        this.todo = data.todo;
        this.loading = false
        this.waittime = 5
        this.timer = setInterval(this.stepInterval, 1000);
        this.update()
        this.updateProgress()
      })
    }

    updateProgress() {
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
        }
        this.bar.animate(0);  // Number from 0.0 to 1.0
        $.get("exercise.cgi?action=eval&id=" + this.parent.exercise_id, (data) => {
          this.evaluating = false
          this.bar.animate((data[0]["correct"]/data[0]["total"]).toFixed(4))
        })
      } else {
        if (!this.progressbar) {
          this.progressbar = new ProgressBar.Line(document.getElementById("progress"), {
            strokeWidth: 4,
            easing: 'easeInOut',
            duration: 1400,
            color: '#FF5500',
            trailColor: '#eee',
            trailWidth: 1,
            svgStyle: {width: '100%', height: '100%'},
            text: {
              style: {
                // Text color.
                // Default: same as stroke color (options.color)
                color: '#999',
                position: 'absolute',
                right: '0',
                top: '10px',
                padding: 0,
                margin: 0,
                transform: null
              },
              autoStyleContainer: false
            },
            from: {color: '#FF5500'},
            to: {color: '#55FF00'},
            step: (state, bar) => {
              bar.setText(Math.round(bar.value() * 100) + ' % done (' + this.todo + ' outliers remaining)');
              bar.path.setAttribute('stroke', state.color);
            }
          });
        }
        this.progressbar.animate(this.progress);
      }
    }
  </script>

</exercise>
