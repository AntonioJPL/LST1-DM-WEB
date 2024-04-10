/**
 * Sctipr for the Drive Monitoriing Website
 * @author Antonio Jose Peñuela Lopez
 * 
 */

const body = document.querySelector("body")

/**
 * Creation of the Summary/Logs section and the interaction between tabs
 */
let contenSection = document.querySelector("div.textData")
contenSection.classList.add("gap-y-3")
let sumSection = document.createElement("div")
sumSection.classList.add("w-[66%]", "self-center")
let divSummary = document.createElement("div")
divSummary.classList.add("w-[50%]", "bg-[#325D88]", "flex", "justify-center", "items-center", "cursor-pointer", "rounded-tl-lg", "transition", "duration-300", "ease-in-out")
let summaryLabel = document.createElement("p")
summaryLabel.classList.add("text-white", "text-xl", "p-2", "pointer-events-none", "select-none")
summaryLabel.appendChild(document.createTextNode("Summary"))
divSummary.appendChild(summaryLabel)
let divLogs = document.createElement("div")
divLogs.classList.add("w-[50%]", "bg-[#6585a6]", "flex", "justify-center", "items-center", "cursor-pointer", "rounded-tr-lg", "transition", "duration-300", "ease-in-out")
let logsLabel = document.createElement("p")
logsLabel.classList.add("text-white", "text-xl", "p-2", "pointer-events-none", "select-none", "transition", "duration-300", "ease-in-out")
logsLabel.appendChild(document.createTextNode("Logs"))
divLogs.appendChild(logsLabel)
let divButtons = document.createElement("div")
divButtons.classList.add("flex", "w-full", "rounded-t-xl")
divButtons.appendChild(divSummary)
divButtons.appendChild(divLogs)
let divContent = document.createElement("div")
divContent.classList.add("flex", "flex-col", "w-full", "border", "border-x-[0.25rem]", "border-b-[0.25rem]", "border-[#325D88]", "overflow-y-scroll", "transition", "duration-300", "ease-in-out", "h-[20rem]", "py-1", "rounded-b-lg")
sumSection.appendChild(divButtons)
sumSection.appendChild(divContent)
contenSection.appendChild(sumSection)

/**
 * Function to fetch the data from mongodb
 */
let data = null;
let filters = null;
let summaryData = null
let selectedFilters = {}

const fetchLatestData = async() => {
    let serverRes = await fetch("http://127.0.0.1:8000/storage/getLogs")
    .then(response => response.json())
    let generalData = await fetch("http://127.0.0.1:8000/storage/getData")
    .then(response => response.json())
    showAllData(generalData.data)
    data = serverRes.data
    filters = serverRes.filters
    summaryData = data.filter(element => element.LogStatus != null)
    startSummary()
    loadFilters()
}

fetchLatestData()

/**
 * Function to generate the Summary and Logs contents
 */
//TODO Implement filters
const logsData = []
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
    prevLine = null
    dataFound = null
    increment = 0
    if(selectedFilters["time"] != "All"){
        while(dataFound == null){
            let element = logsData[increment].split(" ")
            if(element[0].includes(selectedFilters["time"])){
                dataFound = increment
            }
            if(element[0] == "-----------------------"){
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
    }else{
        printAllLogs()
    }
}
const summaryParsedData = []
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
divSummary.addEventListener("click", showSummary)
divLogs.addEventListener("click", showLog)

/**
 * Creation of the Filters section
 */
let filtersSection = document.querySelector("div.filters")
filtersSection.classList.add("w-[25vw]", "fixed", "left-[2rem]", "top-[7.75rem]", "border-r-[#3e3f3a]", "border-r-[0.15rem]", "border-opacity-50", "h-[15rem]", "flex", "flex-col", "items_center")
let filtersCard = document.createElement("div")
filtersCard.classList.add("w-[95%]", "mt-5")
filtersSection.appendChild(filtersCard)
let sectionTitle = document.createElement("h3")
sectionTitle.classList.add("text-lg", "self-center", "text-white", "w-full", "bg-[#325D88]", "rounded-t-lg", "text-center", "py-1")
sectionTitle.appendChild(document.createTextNode("Filters"))
let sectionBody = document.createElement("div")
sectionBody.classList.add("border", "border-[#325D88]", "border-[0.25rem]", "border-t-0", "w-full", "h-[10rem]", "rounded-b-lg", "flex", "flex-col", "items-center")
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
            filters.times[dateInput.value].forEach(time => {
                let option = document.createElement("option")
                option.setAttribute("value", time)
                option.appendChild(document.createTextNode(time))
                timeInput.appendChild(option)
            })
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
        //TODO - Finish filtering the visual contents
        if(operationInput.value != "All" || dateInput.value != "All" || timeInput.value != "All"){
            selectedFilters["operation"] = operationInput.value
            selectedFilters["date"] = dateInput.value
            selectedFilters["time"] = timeInput.value
            if(divLogs.classList.contains("bg-[#325D88]")){
                let evento = new Event("click")
                divLogs.dispatchEvent(evento)
            }
        }else{
            selectedFilters = {}
            divContent.classList.remove("overflow-y-scroll")
            setTimeout(()=>{divContent.classList.add("overflow-y-scroll")}, 1)
            if(divLogs.classList.contains("bg-[#325D88]")){
                printAllLogs()
            }
        }
    })
    let clearButton = document.createElement("button")
    clearButton.classList.add("hover:bg-[#325D88]", "bg-[#6585a6]", "text-white", "font-semibold", "p-2", "rounded-lg", "border-[#325D88]", "border-2", "mt-3", "w-[45%]", "self-center")
    clearButton.appendChild(document.createTextNode("Restore defaults"))
    clearButton.addEventListener("click", (e)=>{
        e.preventDefault()
        selectedFilters = {}
        dateInput.selectedIndex = 0
        operationInput.selectedIndex = 0
        timeInput.innerHTML = ""
        timeInput.appendChild(defaultTime)
        divContent.classList.remove("overflow-y-scroll")
        setTimeout(()=>{divContent.classList.add("overflow-y-scroll")}, 1)
        if(divLogs.classList.contains("bg-[#325D88]")){
           printAllLogs()
        }
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
        graphicContents.classList.add("w-[66%]", "flex", "flex-col", "gap-y-3", "self-center", "graphicSection")
    }else{
        contenSection.removeChild(graphicContents)
    }
    data.forEach(element => {
        let card = document.createElement("div")
        card.classList.add("border-[#325D88]", "border-[0.25rem]", "flex", "flex-col", "rounded-lg")
        let title = document.createElement("h3")
        title.appendChild(document.createTextNode(element.type))
        title.classList.add("py-1", "bg-[#325D88]", "rounded-t-sm", "font-semibold", "text-xl", "text-white", "text-center")
        let summary = document.createElement("section")
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
        })
        let histograms = document.createElement("section")
        histograms.classList.add("flex", "flex-col", "gap-y-2", "my-2")
        let imageArray = [...element.img]
        imageArray.sort((a,b)=>{return a.length - b.length})
        for (let i = 0; i < imageArray.length; i++) {         
            let newImage = document.createElement("img")
            newImage.setAttribute("src", imageArray[i])
            newImage.classList.add("w-[95%]", "h-[25rem]", "self-center")
            histograms.appendChild(newImage)
        }

        card.appendChild(title)
        card.appendChild(summary)
        card.appendChild(histograms)
        graphicContents.appendChild(card)
    });
    contenSection.appendChild(graphicContents)
}

const sortByTime = (a,b) => {
    return new Date(a.Sdate+" "+a.Stime)- new Date(b.Sdate+" "+b.Stime)
}