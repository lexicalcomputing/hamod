<new>
  <div if={status=="loading"} class="valign-wrapper" style="width: 100%; height: 100%">
    <spinner size="big" class="center-align" style="margin: auto"></spinner>
  </div>
  <div if={status=="welcome"}>
    <div class="row">
      <div class="col s12 center-align">
        <h3>Welcome to the outlier detection.</h3>
        <a class="waves-effect waves-light btn-large" style="margin-top: 1em" onclick={onNewExercise}><i class="material-icons left">fiber_new</i>Start new exercise</a>

        <a class="waves-effect waves-light btn-large" style="margin-top: 1em" onclick={onContinueExercise}><i class="material-icons left">restore</i>Continue existing exercise</a>
      </div>
    </div>
  </div>
  <div if={status=="getuser"}>
    <div class="row">
      <div class="col s12 m6">
        <div class="card">
          <div class="card-content">
            <span class="card-title">Start new exercise</span>
            <div class="input-field">
              <i class="material-icons prefix">account_circle</i>
              <input id="name" ref="name" type="text" class="validate" required="" oninput={checkFields}>
              <label class="active" for="name">Your Nick</label>
            </div>
            <div class="input-field">
              <i class="material-icons prefix">language</i>
              <select ref="language" required="" onchange={checkFields}>
                <option value="" disabled selected>Choose your language</option>
                <option value="CS">Czech</option>
                <option value="EN">English</option>
                <option value="ET">Estonian</option>
              </select>
              <label>Select your language</label>
            </div>
          </div>
          <div class="card-action" if={formComplete}>
            <a href="javascript:void(0)" onclick={getNewExercise}>Continue</a>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div if={status=="continue"}>
    <div class="row">
      <div class="col s12 m6">
        <div class="card">
          <div class="card-content">
            <span class="card-title">Continue existing exercise</span>
            <div class="input-field">
              <i class="material-icons prefix">confirmation_number</i>
              <input id="name" ref="exercise_id" type="text" class="validate" required="" pattern="[a-fA-F0-9]\{32\}" oninput={checkExID}>
              <label class="active" for="name">Your unique exercise ID (16 characters)</label>
            </div>
          </div>
          <div class="card-action" if={exIDComplete}>
            <a href="javascript:void(0)" onclick={goExercise}>Continue</a>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div if={status=="start"}>
    <div class="row">
      <div class="col s12">
        <div class="card">
          <div class="card-content">
            <span class="card-title">Welcome {name}</span>
            You are about to start a new exercise. Your exercise ID is <h5>{id}</h5> and 
            you can return to this exercise anytime through this <a href="https://milos.sketchengine.co.uk/outlier_detection/edit/{id}">link</a> or by returning to the main page, choosing to continue an exercise and entering your exercise ID.
            <h5>Your task</h5>
            <ul class="browser-default" style="color: black">
              <li>You will be presented 9 words.</li>
              <li>Your task is to choose an <em>outlier</em> among those words, exactly one word that does not fit the rest of the words according to some cognitive criteria that you should figure out.</li>
              <li>An example set would be: <em>blue, red, green, yellow, orange, black, brown, white, table</em>. Obviously the last word is the outlier: all other are color names.</li>
            </ul>
            <h5>Why should I do that?</h5>
            <ul class="browser-default" style="color: black">
              <li>The dataset will be used for evaluation of automatically built thesauri and by that help improving methods for their automatic generation.</li>
              <li>Examples of distributional thesauri: <a href="https://www.sketchengine.eu/guide/thesaurus-synonyms-antonyms-similar-words/">a word-sketch based one</a> and <a href="https://embeddings.sketchengine.co.uk/">a word-embeddings based one</a>.</li>
              <li>The key reason for taking the task manually is detecting issues in the dataset manifested by low inter-annotator agreement.</li>
            </ul>
            <h5>How long does it take?</h5>
            <ul class="browser-default" style="color: black">
              <li>With the current size of the dataset it only takes about 10 minutes.</li>
            </ul>
            <h5>What happens with the data?</h5>
            <ul class="browser-default" style="color: black">
              <li>The resulting dataset will be openly available under the <a href="https://creativecommons.org/licenses/by-sa/4.0/legalcode">CC-BY-SA 4.0 licence</a> in the <a href="https://github.com/elexis-eu">ELEXIS GitHub repository</a>.</li>
              <li>We are also going to publish anonymized statistics on the inter-annotator agreement evaluation.</li>
              <li>By taking the exercise you agree that the decisions you have made can be stored and used to improve the outlier detection datasets.</li>
            </ul>
            <h5>Can I take the exercise in a language that is not my mother tongue</h5>
            <ul class="browser-default" style="color: black">
              <li>Please don't! While your knowledge of the second language might be excellent, you might not be misled by what actually would be misleading for native speakers.</li>
            </ul>
            <h5>Can I take mutliple turns?</h5>
            <ul class="browser-default" style="color: black">
              <li>Please don't because your next turn could be biased by the data you have already seen.</li>
            </ul>
            <p>
              <label for="agree">
                <input type="checkbox" id="agree" onchange={agreeChanged} ref="agree"/>
                <span class="red-text"><strong>I HAVE READ THIS AND I AGREE</strong></span>
              </label>
            </p>
          </div>
          <div class="card-action" if={agreed}>
            <a href="javascript:void(0)" onclick={startExercise}>Start exercise</a>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    this.status = "welcome";
    this.formComplete = false;
    this.exIDComplete = false;
    this.agreed = false;

    agreeChanged() {
      this.agreed = !!this.refs.agree.checked;
    }
    onNewExercise(e) {
      this.status = "getuser";
      this.update();
      $('select').formSelect();
    }
    onContinueExercise(e) {
      this.status = "continue";
      this.update();
    }
    checkFields(e) {
      var name = this.refs.name.value;
      var lang = this.refs.language.value;
      this.formComplete = (name && lang);
    }
    checkExID(e) {
      this.exIDComplete = this.refs.exercise_id.checkValidity()
    }
    goExercise(e) {
      route("/exercise/" + this.refs.exercise_id.value);
    }
    getNewExercise(e) {
      var name = this.refs.name.value;
      var lang = this.refs.language.value;
      this.status = "loading";
      this.update();
      $.get("exercise.cgi?action=new&name=" + encodeURIComponent(name) + "&lang=" + lang).done((data) => {
        this.status = "start";
        this.name = name;
        this.id = data["id"];
        this.update();
      })
    }
    startExercise(e) {
      route("exercise/" + this.id)
    }
  </script>
</new>
