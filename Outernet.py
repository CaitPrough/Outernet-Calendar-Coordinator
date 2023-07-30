from ics import Calendar
from datetime import timedelta, datetime

def periodsOfActivity(filesICS):
    busySlots = []

    for filePath in filesICS:
        with open(filePath, 'r', encoding="utf-8") as file:
            c = Calendar(file.read())

        for event in c.events:
            busySlots.append((event.begin, event.end))

    return busySlots

def timezoneThing(arrowTime):
    return arrowTime.to('local').naive

def findFreeSlots(filesICS, activityDuration, soonestDate, latestDate):
    busySlots = periodsOfActivity(filesICS)

    allRanges = []
    for start, end in busySlots:
        current = start
        while current < end:
            allRanges.append((timezoneThing(current), timezoneThing(current + timedelta(minutes=1))))
            current += timedelta(minutes=1)

    freePeriods = []
    currentTime = soonestDate
    currentTime = currentTime.replace(tzinfo=None)  # Convert to offset-naive datetime
    currentLatestDate = currentTime + timedelta(minutes=activityDuration)

    while currentLatestDate <= latestDate:
        isBusySlot = any(slot[0] <= currentTime <= slot[1] for slot in allRanges)

        if not isBusySlot:
            # Check if the current slot can be merged with the last slot
            if freePeriods and currentTime == freePeriods[-1][1]:
                freePeriods[-1] = (freePeriods[-1][0], currentLatestDate)
            else:
                freePeriods.append((currentTime, currentLatestDate))

        currentTime += timedelta(minutes=30)
        currentLatestDate += timedelta(minutes=30)

    # Combine adjacent free time slots into one slot
    mergedFreePeriods = []
    for start, end in freePeriods:
        if not mergedFreePeriods or start > mergedFreePeriods[-1][1]:
            mergedFreePeriods.append((start, end))
        else:
            mergedFreePeriods[-1] = (mergedFreePeriods[-1][0], end)

    # Filter out free time slots with a duration less than the desired duration
    mergedFreePeriods = [(start, end) for start, end in mergedFreePeriods if (end - start).total_seconds() >= activityDuration * 60]

    return mergedFreePeriods

if __name__ == "__main__":
    filesICS = ["cait.ics", "caitGmail.ics", "caitOSSM.ics", "caitPrimary.ics", "caitProughMeetings.ics", "communityEvents.ics", "concerts.ics"]  
    activityDuration = 180  # desired duration of the free slot

    # Define the time range you want to search within
    soonestDate = datetime(2023, 7, 30, 10, 0)
    latestDate = datetime(2023, 8, 5, 18, 0)

    freeSlots = findFreeSlots(filesICS, activityDuration, soonestDate, latestDate)

    if freeSlots:
        for i, (start, end) in enumerate(freeSlots, 1):
            print(f"Free time slot {i}: from {start.strftime('%Y-%m-%d %H:%M')} to {end.strftime('%Y-%m-%d %H:%M')}")
    else:
        print("No free time slots found.")
