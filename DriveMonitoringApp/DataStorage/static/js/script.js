/**
 * Sctipr for the Drive Monitoriing Website
 * @author Antonio Jose Peñuela Lopez
 * 
 */

const body = document.querySelector("body")
const title = document.querySelector("title")
const currentUrl = window.location.href

/**
 * Creation of the Summary/Logs section and the interaction between tabs
 */
let contenSection = null
let divSummary = null
let divContent = null
let divLogs = null
let sumSection = null
let summaryLabel = null
let logsLabel = null
let divButtons = null
let data = null;
let filters = null;
let summaryData = null
let selectedFilters = {}
let generalData = {}
let sectionBody = null
let filtersCard = null
let filtersSection = null
let sectionTitle = null
const logsData = []
const summaryParsedData = []

const generateStructure = ()=>{
    contenSection = document.querySelector("div.textData")
    contenSection.innerHTML = ""
    contenSection.classList.add("gap-y-3")
    sumSection = document.createElement("div")
    sumSection.classList.add("w-[66%]", "self-center")
    divSummary = document.createElement("div")
    divSummary.classList.add("w-[50%]", "bg-[#325D88]", "flex", "justify-center", "items-center", "cursor-pointer", "rounded-tl-lg", "transition", "duration-300", "ease-in-out")
    summaryLabel = document.createElement("p")
    summaryLabel.classList.add("text-white", "text-xl", "p-2", "pointer-events-none", "select-none")
    summaryLabel.appendChild(document.createTextNode("Summary"))
    divSummary.appendChild(summaryLabel)
    divLogs = document.createElement("div")
    divLogs.classList.add("w-[50%]", "bg-[#6585a6]", "flex", "justify-center", "items-center", "cursor-pointer", "rounded-tr-lg", "transition", "duration-300", "ease-in-out")
    logsLabel = document.createElement("p")
    logsLabel.classList.add("text-white", "text-xl", "p-2", "pointer-events-none", "select-none", "transition", "duration-300", "ease-in-out")
    logsLabel.appendChild(document.createTextNode("Logs"))
    divLogs.appendChild(logsLabel)
    divButtons = document.createElement("div")
    divButtons.classList.add("flex", "w-full", "rounded-t-xl")
    divButtons.appendChild(divSummary)
    divButtons.appendChild(divLogs)
    divContent = document.createElement("div")
    divContent.classList.add("flex", "flex-col", "w-full", "border", "border-x-[0.25rem]", "border-b-[0.25rem]", "border-[#325D88]", "overflow-y-scroll", "transition", "duration-300", "ease-in-out", "h-[20rem]", "py-1", "rounded-b-lg")
    sumSection.appendChild(divButtons)
    sumSection.appendChild(divContent)
    contenSection.appendChild(sumSection)
    divSummary.addEventListener("click", showSummary)
    divLogs.addEventListener("click", showLog)
}
/**
 * Function to fetch the data from mongodb
 */
const fetchLatestData = async(date = null) => {
    let serverRes = null
    let urlParts = currentUrl.split("/")
    if(urlParts[urlParts.length-1] == "driveMonitoring"){
        summaryParsedData.splice(0, summaryParsedData.length)
        logsData.splice(0, logsData.length)
        if(date != null){
            serverRes = await fetch("http://127.0.0.1:8000/storage/getLogs", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({"date": date})})
            .then(response => response.json())
            generalData = await fetch("http://127.0.0.1:8000/storage/getData", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({"date": date})})
            .then(response => response.json())
        }else{
            serverRes = await fetch("http://127.0.0.1:8000/storage/getLogs")
            .then(response => response.json())
            generalData = await fetch("http://127.0.0.1:8000/storage/getData")
            .then(response => response.json())
        }
        if(generalData.data.Message == null){
            initializeFiltersSection()
            generateStructure()
            showAllData(generalData.data)
            data = serverRes.data
            filters = serverRes.filters
            summaryData = data.filter(element => element.LogStatus != null)
            startInputButtons()
            startSummary()
            loadFilters()
            fillLogs()
        }else{
            console.log(generalData.data.Message)
            contenSection.innerHTML = ""
            filtersSection.innerHTML = ""
            filtersSection.classList = ["filters"]
            filtersSection.classList.add("w-[25vw]", "justify-self-center", "flex", "flex-col", "gap-y-0")
            let divAlert = document.createElement("div")
            divAlert.classList.add("border-red-600", "border-[0.25rem]", "flex", "flex-col", "rounded-lg", "p-3", "text-center", "absolute", "top-[8rem]", "left-[44%]")
            let textAlert = document.createElement("h2")
            textAlert.classList.add("text-xl", "text-red-600")
            textAlert.appendChild(document.createTextNode(generalData.data.Message))
            divAlert.appendChild(textAlert)
            contenSection.appendChild(divAlert)
        }
    }else{
        if(date != null){
            serverRes = await fetch("http://127.0.0.1:8000/storage/getLoadPins", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({"date": date})})
            .then(response => response.json())
        }else{
            serverRes = await fetch("http://127.0.0.1:8000/storage/getLoadPins")
            .then(response => response.json())
        }
        if(serverRes.Message == null){
            startInputButtons()
            startPlotSections()
        }else{
            contenSection.innerHTML = ""
            filtersSection.innerHTML = ""
            filtersSection.classList = ["filters"]
            filtersSection.classList.add("w-[25vw]", "justify-self-center", "flex", "flex-col", "gap-y-0")
            let divAlert = document.createElement("div")
            divAlert.classList.add("border-red-600", "border-[0.25rem]", "flex", "flex-col", "rounded-lg", "p-3", "text-center", "absolute", "top-[8rem]", "left-[44%]")
            let textAlert = document.createElement("h2")
            textAlert.classList.add("text-xl", "text-red-600")
            textAlert.appendChild(document.createTextNode(generalData.data.Message))
            divAlert.appendChild(textAlert)
            contenSection.appendChild(divAlert)
        }
    }

}

fetchLatestData()

/**
 * Function to generate the Summary and Logs contents
 */

const fillLogs = ()=>{
    if(data != null){
        data.forEach(element => {
            if(element.Command == "Park_Out" && element.Status == "command sent" || element.Command == "Park_In" && element.Status == "command sent" || element.Command == "GoToPosition" || element.Command == "Start Tracking"){
                logsData.push("-----------------------")
            }
            if(element.Status != null){
                logsData.push(element.Time+" "+element.Command+" "+element.Status)
            }else{
                logsData.push(element.Time+" "+element.Command)
            }
        });
    }
}
const showLog = (e)=>{
    divContent.scrollTop = 0
    if(logsData.length == 0){
        fillLogs()
    }
    if(e.target.previousSibling.classList.contains("bg-[#325D88]")){
        e.target.previousSibling.classList.remove("bg-[#325D88]")
        e.target.previousSibling.children[0].classList.remove("font-semibold")
        e.target.previousSibling.classList.add("bg-[#6585a6]")
        divLogs.classList.toggle("bg-[#6585a6]")
        divLogs.classList.toggle("bg-[#325D88]")
        logsLabel.classList.add("font-semibold")
        if(Object.keys(selectedFilters).length == 0){
            printAllLogs()
        }else{
            filterLogs()
        }
    }else{
        if(Object.keys(selectedFilters).length > 0){
            filterLogs()
        }else{
            printAllLogs()
        }
    }
    
}
/**
 * Function that prints all the logsData content
 */
const printAllLogs = ()=>{
    divContent.innerHTML = ""
    logsData.forEach(element => {
        if(element != "-----------------------"){
            let parragraph = document.createElement("p")
            parragraph.appendChild(document.createTextNode(element))
            parragraph.classList.add("text-lg", "ms-2")
            divContent.appendChild(parragraph)
        }else{
            let separator = document.createElement("hr")
            separator.classList.add("w-full", "self-center", "my-2", "border-[#325D88]", "border-t-[0.1rem]", "opacity-50")
            divContent.appendChild(separator)
        }
    })
}
/**
 * Function that filters the log to the selected time and shows only thata section
 */
const filterLogs = ()=>{
    divContent.innerHTML = ""
    console.log(selectedFilters["operation"])
    let prevLine = null
    let dataFound = null
    let increment = 0
    if(selectedFilters["time"] != "All"){
        while(dataFound == null){
            let element = logsData[increment].split(" ")
            if (element[0] != "-----------------------"){
                if(selectedFilters["operation"] == "All"){
                    if(element[0].includes(selectedFilters["time"])){
                        dataFound = increment
                    }
                }else{
                    if(element[0] == selectedFilters["time"]){
                        dataFound = increment
                    }else if(element[0][0] == selectedFilters["time"][0] && element[0][1] == selectedFilters["time"][1] && element[0][2] == selectedFilters["time"][2] && element[0][3] == selectedFilters["time"][3] && element[0][4] == selectedFilters["time"][4] && element[0][5] == selectedFilters["time"][5] && element[0][6] == selectedFilters["time"][6]){
                        dataFound = increment
                    }
                }
            }else{
                prevLine = increment
            }
            increment++
        }
        for (let i = prevLine; i < prevLine+100; i++) {
            if(i == logsData.length){
                let separator = document.createElement("hr")
                separator.classList.add("w-full", "self-center", "my-2", "border-[#325D88]", "border-t-[0.1rem]", "opacity-50")
                divContent.appendChild(separator)
                break
            }
            if(logsData[i] == "-----------------------"){
                let separator = document.createElement("hr")
                separator.classList.add("w-full", "self-center", "my-2", "border-[#325D88]", "border-t-[0.1rem]", "opacity-50")
                divContent.appendChild(separator)
                if(i != prevLine){
                    lastLine = i
                    break
                }
            }else{
                if(i == dataFound){
                    let parragraph = document.createElement("p")
                    parragraph.appendChild(document.createTextNode(logsData[i]))
                    parragraph.classList.add("text-lg", "ms-2", "text-[#325D88]", "font-semibold")
                    divContent.appendChild(parragraph)
                }else{
                    let parragraph = document.createElement("p")
                    parragraph.appendChild(document.createTextNode(logsData[i]))
                    parragraph.classList.add("text-lg", "ms-2")
                    divContent.appendChild(parragraph)
                }
            }
        }
    }else if(selectedFilters["operation"] != "All"){
        selectedOption = null

        switch(true){
            case selectedFilters["operation"] == "GoToPos":
                selectedOption = "GoToPosition"
                break
            case selectedFilters["operation"] == "Park-in":
                selectedOption = "Park_In command sent"
                break
            case selectedFilters["operation"] == "Park-out":
                selectedOption = "Park_Out command sent"
                break
            case selectedFilters["operation"] == "Track":
                selectedOption = "Start Tracking"
                break
        }
        let prevLine = null
        logsData.forEach((line, i, array) => {
            if(line.includes(selectedOption) && prevLine == null){
                let separator = document.createElement("hr")
                separator.classList.add("w-full", "self-center", "my-2", "border-[#325D88]", "border-t-[0.1rem]", "opacity-50")
                divContent.appendChild(separator)
                let parragraph = document.createElement("p")
                parragraph.appendChild(document.createTextNode(line))
                parragraph.classList.add("text-lg", "ms-2")
                divContent.appendChild(parragraph)
                prevLine = i-1
            }else if(line == array[0] && prevLine != null){
                prevLine = null
            }else if(prevLine != null){
                let parragraph = document.createElement("p")
                parragraph.appendChild(document.createTextNode(line))
                parragraph.classList.add("text-lg", "ms-2")
                divContent.appendChild(parragraph)
            }
        })
        let separator = document.createElement("hr")
        separator.classList.add("w-full", "self-center", "my-2", "border-[#325D88]", "border-t-[0.1rem]", "opacity-50")
        divContent.appendChild(separator)
    }else{
        printAllLogs()
    }
}

const fillSummary = ()=>{
    if(summaryData != null){
        summaryData.forEach(element =>{
            if(element.LogStatus == "Stopped"){
                summaryParsedData.push(element.Time+" -> "+element.Command+" was "+element.LogStatus.toLowerCase()+" by user")
            }else if(element.LogStatus == "Error"){
                summaryParsedData.push(element.Time+" -> "+element.Command+" had an "+element.LogStatus.toLowerCase())
            }else{
                summaryParsedData.push(element.Time+" -> "+element.Command+" was "+element.LogStatus.toLowerCase())
            }
        })
    }
}
const showSummary = (e)=>{
    divContent.scrollTop = 0
    if(summaryParsedData.length == 0){
        fillSummary()
    }
    if(e.target.nextSibling.classList.contains("bg-[#325D88]")){
        divContent.classList.remove("overflow-y-scroll")
        setTimeout(()=>{divContent.classList.add("overflow-y-scroll")}, 1)
        e.target.nextSibling.classList.remove("bg-[#325D88]")
        e.target.nextSibling.children[0].classList.remove("font-semibold")
        e.target.nextSibling.classList.add("bg-[#6585a6]")
        divSummary.classList.toggle("bg-[#6585a6]")
        divSummary.classList.toggle("bg-[#325D88]")
        summaryLabel.classList.add("font-semibold")
        divContent.innerHTML = ""
        summaryParsedData.forEach(element => {
            let parragraph = document.createElement("p")
            parragraph.appendChild(document.createTextNode(element))
            if(element.includes("error")){
                parragraph.classList.add("text-red-500")
            }else if(!element.includes("by user")){
                parragraph.classList.add("text-black")
            }else{
                parragraph.classList.add("font-semibold")
            }
            parragraph.classList.add("text-lg", "ms-2")
            divContent.appendChild(parragraph)
        })
    }
}
const startSummary = ()=>{
    if(summaryParsedData.length == 0){
        fillSummary()
    }
    summaryParsedData.forEach(element => {
        let parragraph = document.createElement("p")
        parragraph.appendChild(document.createTextNode(element))
        if(element.includes("error")){
            parragraph.classList.add("text-red-500")
        }else if(!element.includes("by user")){
            parragraph.classList.add("text-black")
        }else{
            parragraph.classList.add("font-semibold")
        }
        parragraph.classList.add("text-lg", "ms-2")
        divContent.appendChild(parragraph)
    })
}


/**
 * Creation of the Filters section
 */
const initializeFiltersSection = ()=>{
    filtersSection = document.querySelector("div.filters")
    if(filtersSection == null){
        filtersSection = document.createElement("div")
    }
    filtersSection.innerHTML = ""
    filtersSection.classList.add("w-[25vw]", "fixed", "left-[2rem]", "top-[7.75rem]", "border-r-[#3e3f3a]", "border-r-[0.15rem]", "border-opacity-50", "h-[15rem]", "flex", "flex-col", "items_center")
    filtersCard = document.createElement("div")
    filtersCard.classList.add("w-[95%]", "mt-5")
    filtersSection.appendChild(filtersCard)
    sectionTitle = document.createElement("h3")
    sectionTitle.classList.add("text-lg", "self-center", "text-white", "w-full", "bg-[#325D88]", "rounded-t-lg", "text-center", "py-1")
    sectionTitle.appendChild(document.createTextNode("Filters"))
    sectionBody = document.createElement("div")
    sectionBody.classList.add("border", "border-[#325D88]", "border-[0.25rem]", "border-t-0", "w-full", "h-[10rem]", "rounded-b-lg", "flex", "flex-col", "items-center")
}
/**
 * Function to create the filter form and the inputs
 */
const loadFilters = ()=>{
    let form = document.createElement("form")
    form.classList.add("mt-3", "w-full", "flex", "flex-col", "gap-y-3")
    /**
     * Operation filter and options creation
     */
    let divOperation = document.createElement("div")
    divOperation.classList.add("flex", "gap-x-2", "justify-center")
    let operationLabel = document.createElement("label")
    operationLabel.appendChild(document.createTextNode("Operation: "))
    operationLabel.setAttribute("for", "operation")
    let operationInput = document.createElement("select")
    operationInput.setAttribute("name", "operation")
    operationInput.setAttribute("id", "operation")
    operationInput.classList.add("w-[6.25rem]", "border-[#325D88]", "border-[0.15rem]", "bg-white", "border-opacity-50")
    let defaultOperation = document.createElement("option")
    defaultOperation.appendChild(document.createTextNode("All"))
    defaultOperation.setAttribute("selected", undefined)
    defaultOperation.setAttribute("value", "All")
    operationInput.appendChild(defaultOperation)
    let types = filters.types
    types.forEach(type => {
        let option = document.createElement("option")
        option.setAttribute("value", type)
        option.appendChild(document.createTextNode(type))
        operationInput.appendChild(option)
    });
    divOperation.appendChild(operationLabel)
    divOperation.appendChild(operationInput)
    operationInput.addEventListener("change", ()=>{
        if(operationInput.value != "All"){
            dataFiltered = generalData.data.filter((element)=> element.type == operationInput.value)
            console.log(dataFiltered)
            dateInput.innerHTML = ""
            dateInput.appendChild(defaultDate)
            timeInput.innerHTML = ""
            timeInput.appendChild(defaultTime)
            dataFiltered[0].data.forEach(element =>{
                if(dateInput.children.length == 0){
                    let option = document.createElement("option")
                    option.setAttribute("value", element.Sdate)
                    option.appendChild(document.createTextNode(element.Sdate))
                    dateInput.appendChild(option)
                }else{
                    let foundElements = [].slice.call(dateInput.children).filter(currentElement=> currentElement.value == element.Sdate)
                    if(foundElements.length == 0){
                        let option = document.createElement("option")
                        option.setAttribute("value", element.Sdate)
                        option.appendChild(document.createTextNode(element.Sdate))
                        dateInput.appendChild(option)
                    }
                }
            })
        }else{
            resetFilters(dateInput, defaultDate, timeInput, defaultTime)
        }
    })
    /**
     * Date and time filters creation
     */
    let divDateTime = document.createElement("div")
    divDateTime.classList.add("flex", "justify-evenly")
    let divDate = document.createElement("div")
    divDate.classList.add("flex", "gap-x-2")
    let dateLabel = document.createElement("label")
    dateLabel.appendChild(document.createTextNode("Date: "))
    dateLabel.setAttribute("for", "date")
    let dateInput = document.createElement("select")
    dateInput.setAttribute("name", "date")
    dateInput.setAttribute("id", "date")
    dateInput.classList.add("w-[8.125rem]", "border-[#325D88]", "border-[0.15rem]", "bg-white", "border-opacity-50")
    let defaultDate = document.createElement("option")
    defaultDate.appendChild(document.createTextNode("All"))
    defaultDate.setAttribute("selected", undefined)
    defaultDate.setAttribute("value", "All")
    dateInput.appendChild(defaultDate)
    let dates = filters.dates
    dates.forEach(date => {
        let option = document.createElement("option")
        option.setAttribute("value", date)
        option.appendChild(document.createTextNode(date))
        dateInput.appendChild(option)
    });
    divDate.appendChild(dateLabel)
    divDate.appendChild(dateInput)
    let divTime = document.createElement("div")
    divTime.classList.add("flex", "gap-x-2")
    let timeLabel = document.createElement("label")
    timeLabel.appendChild(document.createTextNode("Time: "))
    timeLabel.setAttribute("for", "time")
    let timeInput = document.createElement("select")
    timeInput.setAttribute("name", "time")
    timeInput.setAttribute("id", "time")
    timeInput.classList.add("w-[8.125rem]", "border-[#325D88]", "border-[0.15rem]", "bg-white", "border-opacity-50")
    let defaultTime = document.createElement("option")
    defaultTime.appendChild(document.createTextNode("Select a date"))
    defaultTime.setAttribute("selected", undefined)
    defaultTime.setAttribute("value", "All")
    timeInput.appendChild(defaultTime)
    divTime.appendChild(timeLabel)
    divTime.appendChild(timeInput)
    divDateTime.appendChild(divDate)
    divDateTime.appendChild(divTime)
    /**
     * Time options on date selection
     */
    dateInput.addEventListener("change", ()=>{
        if(dateInput.value != "All"){
            timeInput.innerHTML = ""
            if(operationInput.value == "All"){
                filters.times[dateInput.value].forEach(time => {
                    let option = document.createElement("option")
                    option.setAttribute("value", time)
                    option.appendChild(document.createTextNode(time))
                    timeInput.appendChild(option)
                })
            }else{
                let filteredTimes = structuredClone(generalData.data.filter((element)=> element.type == operationInput.value))
                filteredTimes = filteredTimes[0].data.filter((element)=> element.Sdate == dateInput.value)
                for (let i = 0; i < filteredTimes.length; i++) {
                    let option = document.createElement("option")
                    option.setAttribute("value", filteredTimes[i].Etime)
                    option.appendChild(document.createTextNode(filteredTimes[i].Etime))
                    timeInput.appendChild(option)
                }

            }
        }else{
            timeInput.innerHTML = ""
            timeInput.appendChild(defaultTime)
        }
    })
    /**
     * Button creation
     */
    let buttons = document.createElement("div")
    buttons.classList.add("flex", "justify-evenly")
    let filterButton = document.createElement("button")
    filterButton.classList.add("hover:bg-[#325D88]", "bg-[#6585a6]", "text-white", "font-semibold", "p-2", "rounded-lg", "border-[#325D88]", "border-2", "mt-3", "w-[45%]", "self-center")
    filterButton.appendChild(document.createTextNode("Filter data"))
    filterButton.addEventListener("click", (e)=>{
        e.preventDefault()
        window.scrollTo({top: 0, left: 0, behavior: "smooth"})
        if(operationInput.value != "All" && dateInput.value != "All" && timeInput.value != "All"){
            selectedFilters["operation"] = operationInput.value
            selectedFilters["date"] = dateInput.value
            selectedFilters["time"] = timeInput.value
            if(divLogs.classList.contains("bg-[#325D88]")){
                let evento = new Event("click")
                divLogs.dispatchEvent(evento)
            }
            let filteredData =  []
            if(selectedFilters["operation"] != "All"){
                filteredData = generalData.data.filter((element) => selectedFilters["operation"] == element.type)
            }
            showAllData(filteredData)
        }else{
            if(operationInput.value != "All" && dateInput.value == "All" && timeInput.value == "All"){
                selectedFilters["operation"] = operationInput.value
                selectedFilters["date"] = dateInput.value
                selectedFilters["time"] = timeInput.value
                filteredData = generalData.data.filter((element) => selectedFilters["operation"] == element.type)
                if(divLogs.classList.contains("bg-[#325D88]")){
                    let evento = new Event("click")
                    divLogs.dispatchEvent(evento)
                }
                showAllData(filteredData)

            }else if(operationInput.value == "All" && dateInput.value != "All" && timeInput.value != "All"){
                selectedFilters["date"] = dateInput.value
                selectedFilters["time"] = timeInput.value
                if(divLogs.classList.contains("bg-[#325D88]")){
                    let evento = new Event("click")
                    divLogs.dispatchEvent(evento)
                }
                let filteredData =  []
                if(selectedFilters["date"] != "All"){
                    filteredData = generalData.data.data.filter((element) => selectedFilters["date"] == element.Sdate)
                }
                if(selectedFilters["time"] != "All"){
                    let found = false
                    for (let i = 0; i < logsData.length; i++) {
                        if(logsData[i] != "-----------------------" && !found){
                            let elementos = logsData[i].split(" ")
                            if(elementos[0] == selectedFilters["time"]){
                                found = true
                            }
                        }else{
                            if(logsData[i] == "-----------------------" && found){
                                let elementos = logsData[i-1].split(" ")
                                filteredData = generalData.data.data.filter((element) => elementos[0] == element.Etime)
                                break
                            }
                        }
                        
                    }
                }
                showAllData(filteredData)
            }else{
                selectedFilters = {}
                divContent.classList.remove("overflow-y-scroll")
                setTimeout(()=>{divContent.classList.add("overflow-y-scroll")}, 1)
                if(divLogs.classList.contains("bg-[#325D88]")){
                    printAllLogs()
                }
                showAllData(generalData.data)
            }
        }
    })
    let clearButton = document.createElement("button")
    clearButton.classList.add("hover:bg-[#325D88]", "bg-[#6585a6]", "text-white", "font-semibold", "p-2", "rounded-lg", "border-[#325D88]", "border-2", "mt-3", "w-[45%]", "self-center")
    clearButton.appendChild(document.createTextNode("Restore defaults"))
    clearButton.addEventListener("click", (e)=>{
        e.preventDefault()
        selectedFilters = {}
        operationInput.selectedIndex = 0
        resetFilters(dateInput, defaultDate, timeInput, defaultTime)
        divContent.classList.remove("overflow-y-scroll")
        setTimeout(()=>{divContent.classList.add("overflow-y-scroll")}, 1)
        if(divLogs.classList.contains("bg-[#325D88]")){
           printAllLogs()
        }
        showAllData(generalData.data)
    })

    buttons.appendChild(filterButton)
    buttons.appendChild(clearButton)
    form.appendChild(divOperation)
    form.appendChild(divDateTime)
    form.appendChild(buttons)
    sectionBody.appendChild(form)
    filtersCard.appendChild(sectionTitle)
    filtersCard.appendChild(sectionBody)
}
/**
 * Function that represents all the data recieved from the database
 */
const showAllData = (data)=>{
    data.sort(sortByTime)
    let graphicContents = document.querySelector("div.graphicSection")
    if( graphicContents == null){
        graphicContents = document.createElement("div")
        graphicContents.classList.add("w-[90%]", "flex", "flex-col", "gap-y-3", "self-center", "graphicSection")
    }else{
        graphicContents.innerHTML = "" 
    }
    data.forEach(element => {
        let card = document.createElement("div")
        card.classList.add("border-[#325D88]", "border-[0.25rem]", "flex", "flex-col", "rounded-lg")
        let title = document.createElement("h3")
        title.appendChild(document.createTextNode(element.type))
        title.classList.add("py-1", "bg-[#325D88]", "rounded-t-sm", "font-semibold", "text-xl", "text-white", "text-center")
        /* let summary = document.createElement("section")
        summary.classList.add("flex", "items-center", "justify-center", "border-b-[#3e3f3a]", "border-b-[0.15rem]", "border-opacity-50", "gap-x-5")
        let labels = ["Start: ", "End: ", "RA: ", "DEC: "]
        labels.forEach(label => {
            let divParragraph = document.createElement("div")
            divParragraph.classList.add("flex", "gap-x-1")
            let pLabel = document.createElement("p")
            pLabel.classList.add("font-semibold", "text-[#3e3f3a]")
            pLabel.appendChild(document.createTextNode(label))
            let pContent = document.createElement("p")
            pContent.classList.add("text-[#3e3f3a]")
            switch(true){
                case label == "RA: ":
                    pContent.appendChild(document.createTextNode(element.RA))
                    break
                case label == "DEC: ":
                    pContent.appendChild(document.createTextNode(element.DEC))
                    break
                case label == "Start: ":
                    pContent.appendChild(document.createTextNode(element.Stime))
                    break
                case label == "End: ":
                    pContent.appendChild(document.createTextNode(element.Etime))
                    break
            }
            if(!((pLabel.innerHTML == "RA: " || pLabel.innerHTML == "DEC: ") && element.RA == null)){
                divParragraph.appendChild(pLabel)
                divParragraph.appendChild(pContent)
            }
            summary.appendChild(divParragraph)
        }) */
        let histograms = document.createElement("section")
        histograms.classList.add("flex", "flex-col", "gap-y-2", "my-2")
        let imageArray = [...element.file]
        imageArray.sort((a,b)=>{return a.length - b.length})
        for (let i = 0; i < imageArray.length; i++) {   
            /*let newImage = document.createElement("img")
            newImage.setAttribute("src", imageArray[i].replace("html", "img").replace(".html", ".png"))
            newImage.classList.add("w-[95%]", "h-[25rem]", "self-center") */
            let newIframe = document.createElement("iframe")
            newIframe.setAttribute("src", imageArray[i])
            newIframe.setAttribute("loading", "lazy")
            newIframe.classList.add("w-[95%]", "h-[25rem]", "self-center")
            if(!imageArray[i].includes("torque") && !imageArray[i].includes("Diff")){
                newIframe.classList.add("order-1")
            }else if(!imageArray[i].includes("Diff")){
                newIframe.classList.add("order-2")
            }else{
                newIframe.classList.add("order-3")
            }
            histograms.appendChild(newIframe)
        }

        card.appendChild(title)
        //card.appendChild(summary)
        card.appendChild(histograms)
        graphicContents.appendChild(card)
    });
    contenSection.appendChild(graphicContents)
}

const sortByTime = (a,b) => {
    return new Date(a.Edate+" "+a.Etime) - new Date(b.Edate+" "+b.Etime)
}
const resetFilters = (dateInput, defaultDate,  timeInput, defaultTime)=>{
    dateInput.innerHTML = ""
    dateInput.appendChild(defaultDate)
    let dates = filters.dates
    dates.forEach(date => {
        let option = document.createElement("option")
        option.setAttribute("value", date)
        option.appendChild(document.createTextNode(date))
        dateInput.appendChild(option)
    });
    timeInput.innerHTML = ""
    timeInput.appendChild(defaultTime)

}
/**
 * Function that adds the interactive buttons to the date input
 */
const startInputButtons = ()=>{
    let div = document.querySelector("div.dateInput")
    if(div.children.length == 2){
        div.classList.add("flex", "flex-row", "items-center", "gap-x-1")
        let backButton = document.createElement("button")
        backButton.classList.add("rounded-xl", "bg-[#325D88]", "back")
        let buttonImage = document.createElement("img")
        buttonImage.setAttribute("src", "static/img/arrow.svg")
        buttonImage.classList.add("size-6", "rotate-180")
        backButton.appendChild(buttonImage)
        let fowardButton = document.createElement("button")
        fowardButton.classList.add("rounded-xl", "bg-[#325D88]", "foward")
        let buttonImage2 = document.createElement("img")
        buttonImage2.setAttribute("src", "static/img/arrow.svg")
        buttonImage2.classList.add("size-6")
        fowardButton.appendChild(buttonImage2)
        let searchButton = document.createElement("button")
        searchButton.classList.add("rounded-xl", "bg-[#325D88]", "search")
        let buttonImage3 = document.createElement("img")
        buttonImage3.setAttribute("src", "static/img/calendarSearch.svg")
        buttonImage3.classList.add("size-6", "p-1")
        searchButton.appendChild(buttonImage3)
        div.appendChild(backButton)
        div.appendChild(fowardButton)
        div.appendChild(searchButton)
        let divChilds = [...div.children]
        let input = null
        divChilds.forEach(child => {
            switch (true) {
                case child.classList.contains("back"):
                    child.classList.add("order-1")
                    break;
                case child.classList.contains("subtitle"):
                    child.classList.add("order-2")
                    break;
                case child.classList.contains("input"):
                    child.classList.add("order-3")
                    input = child
                    break;
                case child.classList.contains("foward"):
                    child.classList.add("order-4")
                    break;
                case child.classList.contains("search"):
                    child.classList.add("order-5")
                    break;
            
            }
        });
        backButton.addEventListener("click", ()=>{
            let value = input.value
            let newDate = new Date(value)
            newDate.setDate(newDate.getDate()-1)
            input.valueAsDate = newDate
        })
        fowardButton.addEventListener("click", ()=>{
            let value = input.value
            let newDate = new Date(value)
            newDate.setDate(newDate.getDate()+1)
            input.valueAsDate = newDate
        })
        searchButton.addEventListener("click", ()=>{
            let value = input.value
            if(generalData.data[0] != undefined){
                if(value != generalData.data[0].data[0]["Sdate"]){
                    changeTitleAndFetch(value)
                }
            }else{
               changeTitleAndFetch(value)
            }
        })
    }
}
const changeTitleAndFetch = (value)=>{
    titleParts = title.innerHTML.split("-")
    title.innerHTML = ""
    title.appendChild(document.createTextNode(titleParts[0]+"-"+titleParts[1]+"-"+value))
    fetchLatestData(value)
}

const startPlotSections = ()=>{
    let plotSection = document.querySelector("div.plotsArea")
    let plotSec1 = document.createElement("div")
    plotSec1.classList.add("border-[#325D88]", "border-[0.25rem]", "flex", "flex-col", "rounded-lg")
    let title = document.createElement("h3")
    title.appendChild(document.createTextNode("10X Cables"))
    title.classList.add("py-1", "bg-[#325D88]", "rounded-t-sm", "font-semibold", "text-xl", "text-white", "text-center")
    plotSec1.appendChild(title)
    let plotSec2 = document.createElement("div")
    plotSec2.classList.add("border-[#325D88]", "border-[0.25rem]", "flex", "flex-col", "rounded-lg")
    let title2 = document.createElement("h3")
    title2.appendChild(document.createTextNode("20X Cables"))
    title2.classList.add("py-1", "bg-[#325D88]", "rounded-t-sm", "font-semibold", "text-xl", "text-white", "text-center")
    plotSec2.appendChild(title2)
    plotSection.appendChild(plotSec1)
    plotSection.appendChild(plotSec2)
}