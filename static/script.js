window.onload = main;
function main(){
  function $(selector) {return document.querySelector(selector)}
  function $$(selector) {return document.querySelectorAll(selector)}
  function c() {
    let numberOfArg = arguments.length;
    for (let i = 0; i < numberOfArg; i++) {
      console.log(arguments[i]);
    }
  }
  c('works');

  // limits input to 250 data points for table and 100 for barchart:
  (function() {
    let chosenInputLimit = $('#limitAmount'), amountLimiter = $('#amountLimiter'), methodSelector = $('#whichmethod'), limit =250 ;

    // prevent the limit to be to high
    function correction() {
      if (chosenInputLimit.value > limit) {
        chosenInputLimit.value = limit;
        amountLimiter.innerHTML = `Let's keep it at ${limit}, right?`;
        amountLimiter.style.color = 'red';
        window.setTimeout(function(){
          amountLimiter.innerHTML = "";
        }, 3000)
      };
    }

    // change the limit if the method changes
    methodSelector.addEventListener('change', function(){
      const method = methodSelector.value;
      switch (method){
        case "json":
          limit = 25000;
          break;
        case "table":
          limit = 250;
          break;
        case "barchart":
          limit = 100;
          break;
        default:
          limit = limit;
      };
      correction();
    });

    // correct input field if limit is too high
    chosenInputLimit.addEventListener('change', correction);

  })();

  // input control : Checks whether weeks are available for a given year:
  let beginWeek = $('#beginDateWeek'), beginYear = $('#beginDateYear'), endWeek = $('#endDateWeek'), endYear = $('#endDateYear');

  // fill array with available weeks(1 - 52) and years (2015 - 2019)
  let weeks = [], years = [], earliestWeekAvailable = 5, latestWeekAvailable = 10;

  (function (){
    for (let i = 0; i < 52; i++) {
      weeks.push({
        option : i + 2,
        text : "Week" + (i + 1),
        value : "Week" + (i + 1),
        selected : false
      })
    }
    for (let i = 2015; i < 2020; i++) {
      years.push({
        intYear : i,
        value : "Year" + i,
        text : i + "",
        selected : false
      })
    }
  })();

  // depending on the year, fill the week dropdown menu with the available weeks.

  let oldWeekForBegin = 1, oldWeekForEnd = 10;

  function addExtraOptions(thisWeek, thisYear) {
    return function (){
      thisWeek.innerHTML = "";

      // if the beginyear is set to 2019, refill both beginweek and endweek
      if (beginYear.value === 'Year2019') {
        beginWeek.innerHTML = "";
        endWeek.innerHTML = "";
      }

      // first and last year dont use every available week
      let optionsToAddBegin = 1, optionsToAddEnd = 53;
      const selectedYear = thisYear.value;
      if (selectedYear === 'Year2015') {
        optionsToAddBegin = earliestWeekAvailable
      }
      else if (selectedYear === "Year2019") {
        optionsToAddEnd = latestWeekAvailable + 1
      }

      // add the options to every year
      weeks.map( selectOption => {
        if (selectOption.option > optionsToAddBegin && selectOption.option <= optionsToAddEnd) {
          if (beginYear.value === 'Year2019') { // prevents bug when setting begin year to the last year available.
            beginWeek.options.add(
              new Option(selectOption.text, selectOption.value, selectOption.selected)
            )
            endWeek.options.add(
              new Option(selectOption.text, selectOption.value, selectOption.selected)
            )
          }
          else {
            thisWeek.options.add(
              new Option(selectOption.text, selectOption.value, selectOption.selected)
            )
          }
        }
      })
      console.log(oldWeekForBegin, oldWeekForEnd);
      setTimeout( () => {endWeek[oldWeekForEnd - 1].selected = true;}, 30);
    }
  };

  // initial weeks available (to lazy to copy and paste the html many times myself)
  window.requestAnimationFrame(addExtraOptions(endWeek, endYear));
  window.requestAnimationFrame(addExtraOptions(beginWeek, beginYear));
  setTimeout( () => {endWeek[latestWeekAvailable -1].selected = true}, 30);

  // whenever a new year is selected, change available weeks
  beginYear.addEventListener("change", addExtraOptions(beginWeek, beginYear));
  endYear.addEventListener("change", addExtraOptions(endWeek, endYear));

  // input control: toggle available years so that the begin can't be before the end


  let oldValueForBegin = 2015, oldValueForEnd = 2019; // track the years that are currently selected

  (function () {
    beginYear.addEventListener("change", function(){
      oldValueForBegin = parseInt(beginYear.value.slice(4,8));
      endYear.innerHTML = ""; // remove old options
      years.map(year => {
        if (oldValueForBegin <= year.intYear) {
          endYear.options.add(
            new Option(year.text, year.value, year.selected)
          )
        }
      window.requestAnimationFrame(addExtraOptions(endWeek, endYear));
      })
      if (oldValueForEnd >= oldValueForBegin) {
        const index = oldValueForEnd - oldValueForBegin;
        endYear.selectedIndex = index; // prevents resetting the other dropdrown menu.
      }
      else {
        oldValueForEnd = oldValueForBegin // prevents bug when setting incompatible years.
      }
    })

    endYear.addEventListener("change", function(){
      oldValueForEnd = +endYear.value.slice(4,8);
    })
  })();

  // input control: toggle available weeks after in the same year.
  (function () {
    // track the weeks that are currently selected.

    beginWeek.addEventListener('change', function(){
      //if (oldValueForEnd !== oldValueForBegin) return
      oldWeekForEnd = parseInt(endWeek.value.slice(4,7));
      endWeek.innerHTML = ""; // remove old options
      oldWeekForBegin = parseInt(beginWeek.value.slice(4,6));
      weeks.map(week => {
        if ((beginYear.value !== "Year2019" || week.option > oldWeekForBegin) && (endYear.value !== 'Year2019' || week.option <= latestWeekAvailable + 1)) {
          endWeek.options.add(
            new Option(week.text, week.value, week.selected)
          )
        }
      })
      if (beginYear.value === endYear.value) {
        if (oldWeekForEnd >= oldWeekForBegin) {
          const index = oldWeekForEnd - oldWeekForBegin;
          endWeek.selectedIndex = index // prevents resetting the other dropdrown menu.
        }
        else {
          oldWeekForEnd = oldWeekForBegin; // prevents bug when setting incompatible weeks.
        }
      }
      else {
        endWeek.selectedIndex = oldWeekForEnd - 1;
      }
    })

    endWeek.addEventListener('change', function(){
      oldWeekForEnd = parseInt(endWeek.value.slice(4,7));
    })
  })();

  // this functions, obviously, gives autocomplete options that are available in the database

  let keypressed = false;

  function autocomplete (box, array, addOptionsHere) {

    keypressed = false;

    // prevent submission momentarily to enable space key for autocomplete
    disableSubmitButton();
    setTimeout(restoreSubmitButton, 2250);

    // create a new div wherein the autocomplete options are given
    let newDivElement = document.createElement("div");
    newDivElement.setAttribute('class', 'autocomplete-items');
    addOptionsHere.parentNode.appendChild(newDivElement);
    const lengthOfArray = array.length;

    // create each row inside the autocomplete option
    for (let i = 0; i < lengthOfArray ; i++) {
      let divFromArray = document.createElement("div");
      divFromArray.innerHTML = array[i] +"<input type='hidden' data-name='" + array[i] + "'>";
      divFromArray.addEventListener('click', function(){
        box.value = array[i];
        closeAllLists();
        setTimeout(restoreSubmitButton, 250);
        window.removeEventListener("keydown", listener);
      })
      // changes color when mouse moves over option to indicate chosen autocomplete option
      divFromArray.addEventListener('mouseover', function(){
        divFromArray.style.backgroundColor = 'grey';
        divFromArray.addEventListener('mouseout', function() {
          divFromArray.style.backgroundColor = $('.container').style.color;
        })
      })

      // color the only autocomplete option when pressing down, autocomplete thereafter when pressing space.
      window.addEventListener("keydown", function listener(event){
        let key = event.keyCode;
        if (keypressed === true && key === 13) {
          divFromArray.style.backgroundColor = $('.container').style.color;
          box.value = array[i];
          closeAllLists();
          setTimeout(restoreSubmitButton, 250);
          window.removeEventListener("keydown", listener);
        }
        else if (key === 40 && !newDivElement[1]) {
          divFromArray.style.backgroundColor = 'grey';
          keypressed = true
        }
      })
      newDivElement.appendChild(divFromArray);
    }
    document.addEventListener('click', function(){
      closeAllLists();
      restoreSubmitButton();
    })
  }

  // prevent submit button during autocomplete
  function disableSubmitButton() {
      $("#submit").type = "button";
  }

  function restoreSubmitButton() {
      $("#submit").type = "submit";
  }

  // remove previous autocomplete options
  function closeAllLists() {
    let letsDeleteThis = $$(".autocomplete-items");
    for (let i = 0; i < letsDeleteThis.length ; i++) {
      letsDeleteThis[i].parentNode.removeChild(letsDeleteThis[i]);
    }
  }

  // autocomplete for chosen artist


  (function() {
    let artistInput = $('#artist'), timeout = null;

    artistInput.addEventListener('input', function(){
      clearTimeout(timeout);

      // get autocomplete array from database if there is no input for 0.3 seconds
      timeout = setTimeout(function() {
        closeAllLists();
        const getInput = artistInput.value;
        if (getInput.length === 0) {
          document.requestAnimationFrame(closeAllLists());
          return
        }
        fetch('/artistchecker/'+getInput)
          .then(function(response) {
          return response.json();
        })
          .then(function(json) {
            autocomplete(artistInput, json, $("#autocomplete-here"));
        });
      }, 300);
    });
  })();

  // autocomplete for chosen album.
  (function() {
    let albumInput = $('#album'), timeout = null;

    albumInput.addEventListener('input', function(){
      clearTimeout(timeout);

      // get autocomplete array from database if there is no input for 0.3 seconds
      timeout = setTimeout(function() {
        closeAllLists();
        let getInput = albumInput.value;
        getInput += '|' + $("#artist").value;
        if (getInput.length === 0) {
          return document.requestAnimationFrame(closeAllLists());
        }
        fetch('/albumchecker/'+getInput)
          .then(function(response) {
          return response.json();
        })
          .then(function(json) {
            autocomplete(albumInput, json, $("#autocomplete-here2"));
        });
      }, 300)
    })
  })();

  // play around with bootstrap classes on resize

  let formController = $$('.formController'), rowMaker = $$('.rowmaker');

  function sizeAdjuster() {

    // for a small screen, turn the scren into three rows of two columns
    if (window.innerWidth <= 768) {
      let lengthOfArray = formController.length;
      for (let i = 0; i < lengthOfArray; i++) {
          formController[i].classList.add("col-6");
      }
      lengthOfArray = rowMaker.length;
      for (let i = 0; i < lengthOfArray; i++) {
          rowMaker[i].classList.add("row");
      }
    }
    // for a larger screen, revert back to normal
    else {
      let lengthOfArray = formController.length;
      for (let i = 0; i < lengthOfArray; i++) {
          formController[i].classList.remove("col-6");
      }
      lengthOfArray = rowMaker.length;
      for (let i = 0; i < lengthOfArray; i++) {
          rowMaker[i].classList.remove("row");
      }
    }
  }
  // fire the screen size adjustment immediatly as well as on each resize
  sizeAdjuster()
  window.addEventListener('resize', sizeAdjuster)
  // toggle input method between barchar, table and json

  let methodInput = $('#whichmethod'), methodOutput = $('#POST-thingy');

  methodInput.addEventListener('change', function(){
    const newMethod = methodInput.value;
    methodOutput.action = "/" + newMethod;
  })
}
