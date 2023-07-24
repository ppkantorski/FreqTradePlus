# 06/04/16 09:35:02
# Author: Shane Stanley
# Adapted by Christopher Stone
# Fixed & Rewritten by CJK
# Modified by ppkantorski
--------------------------------------------------------------------------------

use framework "AppKit"
use scripting additions

property this : a reference to the current application
property nil : a reference to missing value
property _1 : a reference to reference

property NSAlert : a reference to NSAlert of this
property NSDatePicker : a reference to NSDatePicker of this
property NSView : a reference to NSView of this

property NSAlertSecondButtonReturn : 1001
property NSHourMinuteSecondDatePickerElementFlag : 14
property NSTextFieldAndStepperDatePickerStyle : 0
property NSYearMonthDayDatePickerElementFlag : 224
--------------------------------------------------------------------------------
property date : missing value
--------------------------------------------------------------------------------
on run
	its performSelectorOnMainThread:("showDatePicker:") withObject:{¬
		NSTextFieldAndStepperDatePickerStyle, ¬
		NSYearMonthDayDatePickerElementFlag + ¬
		NSHourMinuteSecondDatePickerElementFlag} ¬
		waitUntilDone:true
	
	return my date
	
end run

on showDatePicker:params
	local params
	
	set {PickerStyle, PickerElements} to params
	
	set srcFile to "/var/TMP/.date_prompt_in"
	set allRecords to read srcFile using delimiter "
"
	
	set tmp_index to 0 as integer
	repeat with aRecord in allRecords
		if length of aRecord is greater than 0 then
			if tmp_index is equal to 0 then
				set in_month to aRecord
				log "in_month: " & in_month
			end if
			if tmp_index is equal to 1 then
				set in_day to aRecord
				log "in_day: " & in_day
			end if
			if tmp_index is equal to 2 then
				set in_year to aRecord
				log "in_year: " & in_year
			end if
			if tmp_index is equal to 3 then
				set in_hours to aRecord
				log "in_hours: " & in_hours
			end if
			if tmp_index is equal to 4 then
				set in_minutes to aRecord
				log "in_minutes: " & in_minutes
			end if
			if tmp_index is equal to 5 then
				set message_text to aRecord
				log "message_text: " & message_text
			end if
			if tmp_index is equal to 6 then
				set informative_text to aRecord
				log "informative_text: " & informative_text
			end if
		end if
		set tmp_index to tmp_index + 1
	end repeat
	
	#display dialog tmp_index
	
	tell (current date) to set ¬
		[dateFrom, day, its month, day, year, time] to ¬
		[it, 1, in_month, in_day, in_year, in_hours * hours + in_minutes * minutes]
	
	tell NSDatePicker's alloc()
		initWithFrame_({{0, 0}, {100, 100}})
		setDatePickerStyle_(PickerStyle)
		setDatePickerElements_(PickerElements)
		setDateValue_(dateFrom)
		set fittingSize to fittingSize()
		setFrameSize_(fittingSize)
		
		set View to NSView's alloc()
		View's initWithFrame:{{0, 0}, {100, 175}}
		View's setFrameSize:fittingSize
		View's addSubview:it
		
		tell NSAlert's alloc()
			init()
			setMessageText_(message_text)
			setInformativeText_(informative_text)
			addButtonWithTitle_("OK")
			addButtonWithTitle_("Cancel")
			setAccessoryView_(View)
			
			runModal()
		end tell
		
		set my date to dateValue() as date
		
		set date_text to my date as text
		do shell script "echo  " & quoted form of date_text & " > /var/TMP/.date_prompt_out"
		#do shell script "ftp_date =" & quoted form of date_text
	end tell
end showDatePicker:
