from typing import TypedDict, Union, Optional, Dict, Callable
from streamsync.ui_manager import StreamsyncUI
from streamsync.core_ui import Component
  

RootProps = TypedDict('RootProps', {
    "appName": str,
    "accentColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "emptinessColor": str,
    "containerBackgroundColor": str,
    "containerShadow": str,
    "separatorColor": str,
    "buttonColor": str,
    "buttonTextColor": str,
    "buttonShadow": str,
    "selectedColor": str,
    "cssClasses": str,
    "contentWidth": str,
    "contentHAlign": str,
    "contentVAlign": str,
    "contentPadding": str
}, total=False)

RootEventHandlers = TypedDict('RootEventHandlers', {
    "ss-hashchange": Union[str, Callable]
}, total=False)

PageProps = TypedDict('PageProps', {
    "key": str,
    "pageMode": str,
    "accentColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "emptinessColor": str,
    "containerBackgroundColor": str,
    "containerShadow": str,
    "separatorColor": str,
    "buttonColor": str,
    "buttonTextColor": str,
    "buttonShadow": str,
    "selectedColor": str,
    "cssClasses": str
}, total=False)

PageEventHandlers = TypedDict('PageEventHandlers', {
    "ss-keydown": Union[str, Callable],
    "ss-page-open": Union[str, Callable]
}, total=False)

SidebarProps = TypedDict('SidebarProps', {
    "startCollapsed": str,
    "sidebarBackgroundColor": str,
    "accentColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "containerBackgroundColor": str,
    "containerShadow": str,
    "separatorColor": str,
    "buttonColor": str,
    "buttonTextColor": str,
    "buttonShadow": str,
    "cssClasses": str
}, total=False)

SidebarEventHandlers = TypedDict('SidebarEventHandlers', {
}, total=False)

ButtonProps = TypedDict('ButtonProps', {
    "text": str,
    "isDisabled": str,
    "buttonColor": str,
    "buttonTextColor": str,
    "icon": str,
    "buttonShadow": str,
    "separatorColor": str,
    "cssClasses": str
}, total=False)

ButtonEventHandlers = TypedDict('ButtonEventHandlers', {
    "ss-click": Union[str, Callable]
}, total=False)

TextProps = TypedDict('TextProps', {
    "text": str,
    "useMarkdown": str,
    "alignment": str,
    "primaryTextColor": str,
    "cssClasses": str
}, total=False)

TextEventHandlers = TypedDict('TextEventHandlers', {
    "ss-click": Union[str, Callable]
}, total=False)

SectionProps = TypedDict('SectionProps', {
    "title": str,
    "accentColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "containerBackgroundColor": str,
    "containerShadow": str,
    "separatorColor": str,
    "buttonColor": str,
    "buttonTextColor": str,
    "buttonShadow": str,
    "contentPadding": str,
    "contentHAlign": str,
    "cssClasses": str
}, total=False)

SectionEventHandlers = TypedDict('SectionEventHandlers', {
}, total=False)

HeaderProps = TypedDict('HeaderProps', {
    "text": str,
    "accentColor": str,
    "emptinessColor": str,
    "cssClasses": str
}, total=False)

HeaderEventHandlers = TypedDict('HeaderEventHandlers', {
}, total=False)

HeadingProps = TypedDict('HeadingProps', {
    "text": str,
    "headingType": str,
    "alignment": str,
    "primaryTextColor": str,
    "cssClasses": str
}, total=False)

HeadingEventHandlers = TypedDict('HeadingEventHandlers', {
}, total=False)

DataFrameProps = TypedDict('DataFrameProps', {
    "dataframe": str,
    "showIndex": str,
    "enableSearch": str,
    "enableDownload": str,
    "displayRowCount": Union[float, str],
    "wrapText": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "separatorColor": str,
    "dataframeBackgroundColor": str,
    "dataframeHeaderRowBackgroundColor": str,
    "fontStyle": str,
    "cssClasses": str
}, total=False)

DataFrameEventHandlers = TypedDict('DataFrameEventHandlers', {
}, total=False)

HTMLElementProps = TypedDict('HTMLElementProps', {
    "element": str,
    "styles": Union[Dict, str],
    "attrs": Union[Dict, str],
    "htmlInside": str,
    "cssClasses": str
}, total=False)

HTMLElementEventHandlers = TypedDict('HTMLElementEventHandlers', {
}, total=False)

PaginationProps = TypedDict('PaginationProps', {
    "page": Union[float, str],
    "pageSize": Union[float, str],
    "totalItems": Union[float, str],
    "pageSizeOptions": str,
    "pageSizeShowAll": str,
    "jumpTo": str
}, total=False)

PaginationEventHandlers = TypedDict('PaginationEventHandlers', {
    "ss-change-page": Union[str, Callable],
    "ss-change-page-size": Union[str, Callable]
}, total=False)

RepeaterProps = TypedDict('RepeaterProps', {
    "repeaterObject": Union[Dict, str],
    "keyVariable": str,
    "valueVariable": str
}, total=False)

RepeaterEventHandlers = TypedDict('RepeaterEventHandlers', {
}, total=False)

ColumnProps = TypedDict('ColumnProps', {
    "title": str,
    "width": Union[float, str],
    "isSticky": str,
    "isCollapsible": str,
    "startCollapsed": str,
    "separatorColor": str,
    "contentPadding": str,
    "contentHAlign": str,
    "contentVAlign": str,
    "cssClasses": str
}, total=False)

ColumnEventHandlers = TypedDict('ColumnEventHandlers', {
}, total=False)

ColumnContainerProps = TypedDict('ColumnContainerProps', {
    "cssClasses": str
}, total=False)

ColumnContainerEventHandlers = TypedDict('ColumnContainerEventHandlers', {
}, total=False)

TabProps = TypedDict('TabProps', {
    "name": str,
    "contentPadding": str,
    "contentHAlign": str,
    "cssClasses": str
}, total=False)

TabEventHandlers = TypedDict('TabEventHandlers', {
}, total=False)

TabContainerProps = TypedDict('TabContainerProps', {
    "accentColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "containerBackgroundColor": str,
    "containerShadow": str,
    "separatorColor": str,
    "buttonColor": str,
    "buttonTextColor": str,
    "buttonShadow": str,
    "cssClasses": str
}, total=False)

TabContainerEventHandlers = TypedDict('TabContainerEventHandlers', {
}, total=False)

LinkProps = TypedDict('LinkProps', {
    "url": str,
    "target": str,
    "rel": str,
    "text": str,
    "primaryTextColor": str,
    "cssClasses": str
}, total=False)

LinkEventHandlers = TypedDict('LinkEventHandlers', {
}, total=False)

HorizontalStackProps = TypedDict('HorizontalStackProps', {
    "contentPadding": str,
    "contentHAlign": str,
    "cssClasses": str
}, total=False)

HorizontalStackEventHandlers = TypedDict('HorizontalStackEventHandlers', {
}, total=False)

SeparatorProps = TypedDict('SeparatorProps', {
    "separatorColor": str,
    "cssClasses": str
}, total=False)

SeparatorEventHandlers = TypedDict('SeparatorEventHandlers', {
}, total=False)

ImageProps = TypedDict('ImageProps', {
    "src": str,
    "caption": str,
    "maxWidth": Union[float, str],
    "maxHeight": Union[float, str],
    "secondaryTextColor": str,
    "cssClasses": str
}, total=False)

ImageEventHandlers = TypedDict('ImageEventHandlers', {
    "ss-click": Union[str, Callable]
}, total=False)

PDFProps = TypedDict('PDFProps', {
    "source": str,
    "highlights": Union[Dict, str],
    "selectedMatch": Union[float, str],
    "page": Union[float, str],
    "controls": str,
    "containerBackgroundColor": str,
    "separatorColor": str,
    "primaryTextColor": str,
    "cssClasses": str
}, total=False)

PDFEventHandlers = TypedDict('PDFEventHandlers', {
}, total=False)

IFrameProps = TypedDict('IFrameProps', {
    "src": str,
    "cssClasses": str
}, total=False)

IFrameEventHandlers = TypedDict('IFrameEventHandlers', {
    "ss-load": Union[str, Callable]
}, total=False)

GoogleMapsProps = TypedDict('GoogleMapsProps', {
    "apiKey": str,
    "mapId": str,
    "mapType": str,
    "zoom": Union[float, str],
    "lat": Union[float, str],
    "lng": Union[float, str],
    "markers": Union[Dict, str],
    "cssClasses": str
}, total=False)

GoogleMapsEventHandlers = TypedDict('GoogleMapsEventHandlers', {
    "gmap-marker-click": Union[str, Callable],
    "gmap-click": Union[str, Callable]
}, total=False)

MapboxProps = TypedDict('MapboxProps', {
    "accessToken": str,
    "mapStyle": str,
    "zoom": Union[float, str],
    "lat": Union[float, str],
    "lng": Union[float, str],
    "markers": Union[Dict, str],
    "controls": str,
    "cssClasses": str
}, total=False)

MapboxEventHandlers = TypedDict('MapboxEventHandlers', {
    "mapbox-marker-click": Union[str, Callable],
    "mapbox-click": Union[str, Callable]
}, total=False)

IconProps = TypedDict('IconProps', {
    "icon": str,
    "size": Union[float, str],
    "color": str,
    "cssClasses": str
}, total=False)

IconEventHandlers = TypedDict('IconEventHandlers', {
}, total=False)

TimerProps = TypedDict('TimerProps', {
    "intervalMs": Union[float, str],
    "isActive": str,
    "accentColor": str,
    "cssClasses": str
}, total=False)

TimerEventHandlers = TypedDict('TimerEventHandlers', {
    "ss-tick": Union[str, Callable]
}, total=False)

TextInputProps = TypedDict('TextInputProps', {
    "label": str,
    "placeholder": str,
    "passwordMode": str,
    "cssClasses": str
}, total=False)

TextInputEventHandlers = TypedDict('TextInputEventHandlers', {
    "ss-change": Union[str, Callable],
    "ss-change-finish": Union[str, Callable]
}, total=False)

TextareaInputProps = TypedDict('TextareaInputProps', {
    "label": str,
    "placeholder": str,
    "rows": Union[float, str],
    "cssClasses": str
}, total=False)

TextareaInputEventHandlers = TypedDict('TextareaInputEventHandlers', {
    "ss-change": Union[str, Callable],
    "ss-change-finish": Union[str, Callable]
}, total=False)

NumberInputProps = TypedDict('NumberInputProps', {
    "label": str,
    "placeholder": str,
    "minValue": Union[float, str],
    "maxValue": Union[float, str],
    "valueStep": Union[float, str],
    "cssClasses": str
}, total=False)

NumberInputEventHandlers = TypedDict('NumberInputEventHandlers', {
    "ss-number-change": Union[str, Callable],
    "ss-number-change-finish": Union[str, Callable]
}, total=False)

SliderInputProps = TypedDict('SliderInputProps', {
    "label": str,
    "minValue": Union[float, str],
    "maxValue": Union[float, str],
    "stepSize": Union[float, str],
    "cssClasses": str
}, total=False)

SliderInputEventHandlers = TypedDict('SliderInputEventHandlers', {
    "ss-number-change": Union[str, Callable]
}, total=False)

DateInputProps = TypedDict('DateInputProps', {
    "label": str,
    "cssClasses": str
}, total=False)

DateInputEventHandlers = TypedDict('DateInputEventHandlers', {
    "ss-date-change": Union[str, Callable]
}, total=False)

RadioInputProps = TypedDict('RadioInputProps', {
    "label": str,
    "options": Union[Dict, str],
    "orientation": str,
    "cssClasses": str
}, total=False)

RadioInputEventHandlers = TypedDict('RadioInputEventHandlers', {
    "ss-option-change": Union[str, Callable]
}, total=False)

CheckboxInputProps = TypedDict('CheckboxInputProps', {
    "label": str,
    "options": Union[Dict, str],
    "orientation": str,
    "cssClasses": str
}, total=False)

CheckboxInputEventHandlers = TypedDict('CheckboxInputEventHandlers', {
    "ss-options-change": Union[str, Callable]
}, total=False)

DropdownInputProps = TypedDict('DropdownInputProps', {
    "label": str,
    "options": Union[Dict, str],
    "cssClasses": str
}, total=False)

DropdownInputEventHandlers = TypedDict('DropdownInputEventHandlers', {
    "ss-option-change": Union[str, Callable]
}, total=False)

SelectInputProps = TypedDict('SelectInputProps', {
    "label": str,
    "options": Union[Dict, str],
    "placeholder": str,
    "maximumCount": Union[float, str],
    "accentColor": str,
    "chipTextColor": str,
    "selectedColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "containerBackgroundColor": str,
    "separatorColor": str,
    "cssClasses": str
}, total=False)

SelectInputEventHandlers = TypedDict('SelectInputEventHandlers', {
    "ss-option-change": Union[str, Callable]
}, total=False)

MultiselectInputProps = TypedDict('MultiselectInputProps', {
    "label": str,
    "options": Union[Dict, str],
    "placeholder": str,
    "maximumCount": Union[float, str],
    "accentColor": str,
    "chipTextColor": str,
    "selectedColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "containerBackgroundColor": str,
    "separatorColor": str,
    "cssClasses": str
}, total=False)

MultiselectInputEventHandlers = TypedDict('MultiselectInputEventHandlers', {
    "ss-options-change": Union[str, Callable]
}, total=False)

FileInputProps = TypedDict('FileInputProps', {
    "label": str,
    "allowMultipleFiles": str,
    "cssClasses": str
}, total=False)

FileInputEventHandlers = TypedDict('FileInputEventHandlers', {
    "ss-file-change": Union[str, Callable]
}, total=False)

WebcamCaptureProps = TypedDict('WebcamCaptureProps', {
    "refreshRate": Union[float, str],
    "buttonColor": str,
    "buttonTextColor": str,
    "buttonShadow": str,
    "separatorColor": str,
    "cssClasses": str
}, total=False)

WebcamCaptureEventHandlers = TypedDict('WebcamCaptureEventHandlers', {
    "ss-webcam": Union[str, Callable]
}, total=False)

VegaLiteChartProps = TypedDict('VegaLiteChartProps', {
    "spec": Union[Dict, str],
    "cssClasses": str
}, total=False)

VegaLiteChartEventHandlers = TypedDict('VegaLiteChartEventHandlers', {
}, total=False)

PlotlyGraphProps = TypedDict('PlotlyGraphProps', {
    "spec": Union[Dict, str],
    "cssClasses": str
}, total=False)

PlotlyGraphEventHandlers = TypedDict('PlotlyGraphEventHandlers', {
    "plotly-click": Union[str, Callable],
    "plotly-selected": Union[str, Callable],
    "plotly-deselect": Union[str, Callable]
}, total=False)

MetricProps = TypedDict('MetricProps', {
    "name": str,
    "metricValue": str,
    "description": str,
    "note": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "positiveColor": str,
    "neutralColor": str,
    "negativeColor": str,
    "cssClasses": str
}, total=False)

MetricEventHandlers = TypedDict('MetricEventHandlers', {
}, total=False)

MessageProps = TypedDict('MessageProps', {
    "message": str,
    "successColor": str,
    "errorColor": str,
    "warningColor": str,
    "infoColor": str,
    "loadingColor": str,
    "primaryTextColor": str,
    "cssClasses": str
}, total=False)

MessageEventHandlers = TypedDict('MessageEventHandlers', {
}, total=False)

VideoPlayerProps = TypedDict('VideoPlayerProps', {
    "src": str,
    "controls": str,
    "autoplay": str,
    "loop": str,
    "muted": str,
    "cssClasses": str
}, total=False)

VideoPlayerEventHandlers = TypedDict('VideoPlayerEventHandlers', {
}, total=False)

ChatProps = TypedDict('ChatProps', {
    "incomingInitials": str,
    "outgoingInitials": str,
    "useMarkdown": str,
    "enableFileUpload": str,
    "placeholder": str,
    "incomingColor": str,
    "outgoingColor": str,
    "avatarBackgroundColor": str,
    "avatarTextColor": str,
    "containerBackgroundColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "separatorColor": str,
    "buttonColor": str,
    "buttonTextColor": str,
    "cssClasses": str
}, total=False)

ChatEventHandlers = TypedDict('ChatEventHandlers', {
    "ss-chat-message": Union[str, Callable],
    "ss-chat-action-click": Union[str, Callable],
    "ss-file-change": Union[str, Callable]
}, total=False)

StepProps = TypedDict('StepProps', {
    "name": str,
    "contentPadding": str,
    "isCompleted": str,
    "contentHAlign": str,
    "cssClasses": str
}, total=False)

StepEventHandlers = TypedDict('StepEventHandlers', {
}, total=False)

StepContainerProps = TypedDict('StepContainerProps', {
    "accentColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "containerBackgroundColor": str,
    "containerShadow": str,
    "separatorColor": str,
    "buttonColor": str,
    "buttonTextColor": str,
    "buttonShadow": str,
    "cssClasses": str
}, total=False)

StepContainerEventHandlers = TypedDict('StepContainerEventHandlers', {
}, total=False)

RatingInputProps = TypedDict('RatingInputProps', {
    "label": str,
    "feedback": str,
    "minValue": Union[float, str],
    "maxValue": Union[float, str],
    "valueStep": Union[float, str],
    "accentColor": str,
    "primaryTextColor": str,
    "cssClasses": str
}, total=False)

RatingInputEventHandlers = TypedDict('RatingInputEventHandlers', {
    "ss-number-change": Union[str, Callable]
}, total=False)

TagsProps = TypedDict('TagsProps', {
    "tags": Union[Dict, str],
    "referenceColor": str,
    "seed": Union[float, str],
    "rotateHue": str,
    "primaryTextColor": str,
    "cssClasses": str
}, total=False)

TagsEventHandlers = TypedDict('TagsEventHandlers', {
    "ss-tag-click": Union[str, Callable]
}, total=False)

SwitchInputProps = TypedDict('SwitchInputProps', {
    "label": str,
    "accentColor": str,
    "primaryTextColor": str,
    "separatorColor": str,
    "cssClasses": str
}, total=False)

SwitchInputEventHandlers = TypedDict('SwitchInputEventHandlers', {
    "ss-toggle": Union[str, Callable]
}, total=False)

class StreamsyncUIManager(StreamsyncUI):
    """The StreamsyncUIManager class is intended to include dynamically-
    generated methods corresponding to UI components defined in the Vue
    frontend during the build process.

    This class serves as a bridge for programmatically interacting with the
    frontend, allowing methods to adapt to changes in the UI components without
    manual updates.
    """

    # Hardcoded classes for proof-of-concept purposes
  
    def Root(self, 
            content: RootProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[RootEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        The root component of the application, which serves as the starting point of the component hierarchy.
        """
        defaultContent: RootProps = {
            "selectedColor": "rgba(210, 234, 244, 0.8)",
            "contentWidth": "100%",
            "contentHAlign": "unset",
            "contentVAlign": "unset",
            "contentPadding": "0",
        }
        content = defaultContent | content
        component = self.create_container_component(
            'root',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Page(self, 
            content: PageProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[PageEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A container component representing a single page within the application.
        """
        defaultContent: PageProps = {
            "pageMode": "compact",
            "selectedColor": "rgba(210, 234, 244, 0.8)",
        }
        content = defaultContent | content
        component = self.create_container_component(
            'page',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Sidebar(self, 
            content: SidebarProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[SidebarEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A container component that organises its children in a sidebar. Its parent must be a Page component.
        """
        defaultContent: SidebarProps = {
            "startCollapsed": "no",
            "sidebarBackgroundColor": "rgba(255, 255, 255, 0.3)",
        }
        content = defaultContent | content
        component = self.create_container_component(
            'sidebar',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Button(self, 
            content: ButtonProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[ButtonEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A standalone button component that can be linked to a click event handler.
        """
        defaultContent: ButtonProps = {
            "isDisabled": "no",
        }
        content = defaultContent | content
        component = self.create_component(
            'button',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Text(self, 
            content: TextProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[TextEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A component to display plain text or formatted text using Markdown syntax.
        """
        defaultContent: TextProps = {
            "text": "(No text)",
            "useMarkdown": "no",
            "alignment": "left",
        }
        content = defaultContent | content
        component = self.create_component(
            'text',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Section(self, 
            content: SectionProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[SectionEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A container component that divides the layout into sections, with an optional title.
        """
        defaultContent: SectionProps = {
            "contentPadding": "16px",
            "contentHAlign": "unset",
        }
        content = defaultContent | content
        component = self.create_container_component(
            'section',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Header(self, 
            content: HeaderProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[HeaderEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A container component that typically contains the main navigation elements.
        """
        defaultContent: HeaderProps = {
            "text": "(No text)",
        }
        content = defaultContent | content
        component = self.create_container_component(
            'header',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Heading(self, 
            content: HeadingProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[HeadingEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A text component used to display headings or titles in different sizes and styles.
        """
        defaultContent: HeadingProps = {
            "text": "(No text)",
            "headingType": "h2",
            "alignment": "left",
        }
        content = defaultContent | content
        component = self.create_component(
            'heading',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def DataFrame(self, 
            content: DataFrameProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[DataFrameEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A component to display Pandas DataFrames.
        """
        defaultContent: DataFrameProps = {
            "dataframe": "data:application/vnd.apache.arrow.file;base64,QVJST1cxAAD/////iAMAABAAAAAAAAoADgAGAAUACAAKAAAAAAEEABAAAAAAAAoADAAAAAQACAAKAAAAlAIAAAQAAAABAAAADAAAAAgADAAEAAgACAAAAGwCAAAEAAAAXwIAAHsiaW5kZXhfY29sdW1ucyI6IFsiX19pbmRleF9sZXZlbF8wX18iXSwgImNvbHVtbl9pbmRleGVzIjogW3sibmFtZSI6IG51bGwsICJmaWVsZF9uYW1lIjogbnVsbCwgInBhbmRhc190eXBlIjogInVuaWNvZGUiLCAibnVtcHlfdHlwZSI6ICJvYmplY3QiLCAibWV0YWRhdGEiOiB7ImVuY29kaW5nIjogIlVURi04In19XSwgImNvbHVtbnMiOiBbeyJuYW1lIjogImNvbF9hIiwgImZpZWxkX25hbWUiOiAiY29sX2EiLCAicGFuZGFzX3R5cGUiOiAiaW50NjQiLCAibnVtcHlfdHlwZSI6ICJpbnQ2NCIsICJtZXRhZGF0YSI6IG51bGx9LCB7Im5hbWUiOiAiY29sX2IiLCAiZmllbGRfbmFtZSI6ICJjb2xfYiIsICJwYW5kYXNfdHlwZSI6ICJpbnQ2NCIsICJudW1weV90eXBlIjogImludDY0IiwgIm1ldGFkYXRhIjogbnVsbH0sIHsibmFtZSI6IG51bGwsICJmaWVsZF9uYW1lIjogIl9faW5kZXhfbGV2ZWxfMF9fIiwgInBhbmRhc190eXBlIjogImludDY0IiwgIm51bXB5X3R5cGUiOiAiaW50NjQiLCAibWV0YWRhdGEiOiBudWxsfV0sICJjcmVhdG9yIjogeyJsaWJyYXJ5IjogInB5YXJyb3ciLCAidmVyc2lvbiI6ICIxMi4wLjAifSwgInBhbmRhc192ZXJzaW9uIjogIjEuNS4zIn0ABgAAAHBhbmRhcwAAAwAAAIgAAABEAAAABAAAAJT///8AAAECEAAAACQAAAAEAAAAAAAAABEAAABfX2luZGV4X2xldmVsXzBfXwAAAJD///8AAAABQAAAAND///8AAAECEAAAABgAAAAEAAAAAAAAAAUAAABjb2xfYgAAAMD///8AAAABQAAAABAAFAAIAAYABwAMAAAAEAAQAAAAAAABAhAAAAAgAAAABAAAAAAAAAAFAAAAY29sX2EAAAAIAAwACAAHAAgAAAAAAAABQAAAAAAAAAD/////6AAAABQAAAAAAAAADAAWAAYABQAIAAwADAAAAAADBAAYAAAAMAAAAAAAAAAAAAoAGAAMAAQACAAKAAAAfAAAABAAAAACAAAAAAAAAAAAAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAQAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAABAAAAAAAAAAAAAAAAMAAAACAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAIAAAAAAAAAAwAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAD/////AAAAABAAAAAMABQABgAIAAwAEAAMAAAAAAAEADwAAAAoAAAABAAAAAEAAACYAwAAAAAAAPAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAACgAMAAAABAAIAAoAAACUAgAABAAAAAEAAAAMAAAACAAMAAQACAAIAAAAbAIAAAQAAABfAgAAeyJpbmRleF9jb2x1bW5zIjogWyJfX2luZGV4X2xldmVsXzBfXyJdLCAiY29sdW1uX2luZGV4ZXMiOiBbeyJuYW1lIjogbnVsbCwgImZpZWxkX25hbWUiOiBudWxsLCAicGFuZGFzX3R5cGUiOiAidW5pY29kZSIsICJudW1weV90eXBlIjogIm9iamVjdCIsICJtZXRhZGF0YSI6IHsiZW5jb2RpbmciOiAiVVRGLTgifX1dLCAiY29sdW1ucyI6IFt7Im5hbWUiOiAiY29sX2EiLCAiZmllbGRfbmFtZSI6ICJjb2xfYSIsICJwYW5kYXNfdHlwZSI6ICJpbnQ2NCIsICJudW1weV90eXBlIjogImludDY0IiwgIm1ldGFkYXRhIjogbnVsbH0sIHsibmFtZSI6ICJjb2xfYiIsICJmaWVsZF9uYW1lIjogImNvbF9iIiwgInBhbmRhc190eXBlIjogImludDY0IiwgIm51bXB5X3R5cGUiOiAiaW50NjQiLCAibWV0YWRhdGEiOiBudWxsfSwgeyJuYW1lIjogbnVsbCwgImZpZWxkX25hbWUiOiAiX19pbmRleF9sZXZlbF8wX18iLCAicGFuZGFzX3R5cGUiOiAiaW50NjQiLCAibnVtcHlfdHlwZSI6ICJpbnQ2NCIsICJtZXRhZGF0YSI6IG51bGx9XSwgImNyZWF0b3IiOiB7ImxpYnJhcnkiOiAicHlhcnJvdyIsICJ2ZXJzaW9uIjogIjEyLjAuMCJ9LCAicGFuZGFzX3ZlcnNpb24iOiAiMS41LjMifQAGAAAAcGFuZGFzAAADAAAAiAAAAEQAAAAEAAAAlP///wAAAQIQAAAAJAAAAAQAAAAAAAAAEQAAAF9faW5kZXhfbGV2ZWxfMF9fAAAAkP///wAAAAFAAAAA0P///wAAAQIQAAAAGAAAAAQAAAAAAAAABQAAAGNvbF9iAAAAwP///wAAAAFAAAAAEAAUAAgABgAHAAwAAAAQABAAAAAAAAECEAAAACAAAAAEAAAAAAAAAAUAAABjb2xfYQAAAAgADAAIAAcACAAAAAAAAAFAAAAAsAMAAEFSUk9XMQ==",
            "showIndex": "yes",
            "enableSearch": "no",
            "enableDownload": "no",
            "displayRowCount": "10",
            "wrapText": "no",
            "dataframeBackgroundColor": "#ffffff",
            "dataframeHeaderRowBackgroundColor": "#f0f0f0",
            "fontStyle": "normal",
        }
        content = defaultContent | content
        component = self.create_component(
            'dataframe',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def HTMLElement(self, 
            content: HTMLElementProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[HTMLElementEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A generic component that creates customisable HTML elements, which can serve as containers for other components.
        """
        defaultContent: HTMLElementProps = {
            "element": "div",
            "styles": "",
            "attrs": "",
            "htmlInside": "",
        }
        content = defaultContent | content
        component = self.create_container_component(
            'html',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Pagination(self, 
            content: PaginationProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[PaginationEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A component that can help you paginate records, for example from a Repeater or a DataFrame.
        """
        defaultContent: PaginationProps = {
            "page": "1",
            "pageSize": "10",
            "totalItems": "10",
            "pageSizeOptions": "",
            "pageSizeShowAll": "no",
            "jumpTo": "no",
        }
        content = defaultContent | content
        component = self.create_component(
            'pagination',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Repeater(self, 
            content: RepeaterProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[RepeaterEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A container component that repeats its child components based on a dictionary.
        """
        defaultContent: RepeaterProps = {
            "repeaterObject": "{\n  \"a\": {\n    \"desc\": \"Option A\"\n  },\n  \"b\": {\n    \"desc\": \"Option B\"\n  }\n}",
            "keyVariable": "itemId",
            "valueVariable": "item",
        }
        content = defaultContent | content
        component = self.create_container_component(
            'repeater',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Column(self, 
            content: ColumnProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[ColumnEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A layout component that organises its child components in columns. Must be inside a Column Container component.
        """
        defaultContent: ColumnProps = {
            "width": "1",
            "isSticky": "no",
            "isCollapsible": "no",
            "startCollapsed": "no",
            "contentPadding": "0",
            "contentHAlign": "unset",
            "contentVAlign": "unset",
        }
        content = defaultContent | content
        component = self.create_container_component(
            'column',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def ColumnContainer(self, 
            content: ColumnContainerProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[ColumnContainerEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        Serves as container for Column components
        """
        defaultContent: ColumnContainerProps = {

        }
        content = defaultContent | content
        component = self.create_container_component(
            'columns',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Tab(self, 
            content: TabProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[TabEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A container component that displays its child components as a tab inside a Tab Container.
        """
        defaultContent: TabProps = {
            "name": "(No name)",
            "contentPadding": "16px",
            "contentHAlign": "unset",
        }
        content = defaultContent | content
        component = self.create_container_component(
            'tab',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def TabContainer(self, 
            content: TabContainerProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[TabContainerEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A container component for organising and displaying Tab components in a tabbed interface.
        """
        defaultContent: TabContainerProps = {

        }
        content = defaultContent | content
        component = self.create_container_component(
            'tabs',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Link(self, 
            content: LinkProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[LinkEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A component to create a hyperlink.
        """
        defaultContent: LinkProps = {
            "url": "https://streamsync.cloud",
            "target": "_self",
            "text": "",
        }
        content = defaultContent | content
        component = self.create_component(
            'link',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def HorizontalStack(self, 
            content: HorizontalStackProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[HorizontalStackEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A layout component that stacks its child components horizontally, wrapping them to the next row if necessary.
        """
        defaultContent: HorizontalStackProps = {
            "contentPadding": "0",
            "contentHAlign": "unset",
        }
        content = defaultContent | content
        component = self.create_container_component(
            'horizontalstack',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Separator(self, 
            content: SeparatorProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[SeparatorEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A visual component to create a separation between adjacent elements.
        """
        defaultContent: SeparatorProps = {

        }
        content = defaultContent | content
        component = self.create_component(
            'separator',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Image(self, 
            content: ImageProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[ImageEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A component to display images.
        """
        defaultContent: ImageProps = {
            "src": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjMwIiBoZWlnaHQ9IjIzMCIgdmlld0JveD0iMCAwIDIzMCAyMzAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMzAiIGhlaWdodD0iMjMwIiBmaWxsPSIjREFEQURBIi8+CjxyZWN0IHg9Ijg2LjA0MzkiIHk9Ijc4IiB3aWR0aD0iNzEuMjkzNyIgaGVpZ2h0PSIzNC42NDY3IiByeD0iMTcuMzIzMyIgZmlsbD0id2hpdGUiIHN0cm9rZT0id2hpdGUiLz4KPHJlY3QgeD0iNzIuNSIgeT0iMTEzLjY5MyIgd2lkdGg9IjcwLjI5MzciIGhlaWdodD0iMzYuODA3MyIgcng9IjE3LjUiIGZpbGw9IndoaXRlIiBzdHJva2U9IndoaXRlIi8+Cjwvc3ZnPgo=",
            "maxWidth": "-1",
            "maxHeight": "-1",
        }
        content = defaultContent | content
        component = self.create_component(
            'image',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def PDF(self, 
            content: PDFProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[PDFEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A component to embed PDF documents.
        """
        defaultContent: PDFProps = {
            "highlights": "[]",
            "selectedMatch": "",
            "controls": "yes",
        }
        content = defaultContent | content
        component = self.create_component(
            'pdf',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def IFrame(self, 
            content: IFrameProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[IFrameEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A component to embed an external resource in an iframe.
        """
        defaultContent: IFrameProps = {
            "src": "",
        }
        content = defaultContent | content
        component = self.create_component(
            'iframe',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def GoogleMaps(self, 
            content: GoogleMapsProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[GoogleMapsEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A component to embed a Google Map. It can be used to display a map with markers.
        """
        defaultContent: GoogleMapsProps = {
            "apiKey": "",
            "mapId": "",
            "mapType": "roadmap",
            "zoom": "8",
            "lat": "37.79322359164316",
            "lng": "-122.39999318828129",
            "markers": "[{\"lat\":37.79322359164316,\"lng\":-122.39999318828129,\"name\":\"Marker\"}]",
        }
        content = defaultContent | content
        component = self.create_component(
            'googlemaps',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Mapbox(self, 
            content: MapboxProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[MapboxEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A component to embed a Mapbox map. It can be used to display a map with markers.
        """
        defaultContent: MapboxProps = {
            "accessToken": "",
            "mapStyle": "mapbox://styles/mapbox/standard",
            "zoom": "8",
            "lat": "37.79322359164316",
            "lng": "-122.39999318828129",
            "controls": "yes",
        }
        content = defaultContent | content
        component = self.create_component(
            'mapbox',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Icon(self, 
            content: IconProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[IconEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A component to display an icon
        """
        defaultContent: IconProps = {
            "icon": "square-line",
            "size": "14",
        }
        content = defaultContent | content
        component = self.create_component(
            'icon',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Timer(self, 
            content: TimerProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[TimerEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A component that emits an event repeatedly at specified time intervals, enabling time-based refresh.
        """
        defaultContent: TimerProps = {
            "intervalMs": "200",
            "isActive": "yes",
        }
        content = defaultContent | content
        component = self.create_component(
            'timer',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def TextInput(self, 
            content: TextInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[TextInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A user input component that allows users to enter single-line text values.
        """
        defaultContent: TextInputProps = {
            "passwordMode": "no",
        }
        content = defaultContent | content
        component = self.create_component(
            'textinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def TextareaInput(self, 
            content: TextareaInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[TextareaInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A user input component that allows users to enter multi-line text values.
        """
        defaultContent: TextareaInputProps = {
            "rows": "5",
        }
        content = defaultContent | content
        component = self.create_component(
            'textareainput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def NumberInput(self, 
            content: NumberInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[NumberInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A user input component that allows users to enter numeric values.
        """
        defaultContent: NumberInputProps = {
            "minValue": "",
            "maxValue": "",
            "valueStep": "1",
        }
        content = defaultContent | content
        component = self.create_component(
            'numberinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def SliderInput(self, 
            content: SliderInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[SliderInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A user input component that allows users to select numeric values using a slider with optional constraints like min, max, and step.
        """
        defaultContent: SliderInputProps = {
            "minValue": "0",
            "maxValue": "100",
            "stepSize": "1",
        }
        content = defaultContent | content
        component = self.create_component(
            'sliderinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def DateInput(self, 
            content: DateInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[DateInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A user input component that allows users to select a date using a date picker interface.
        """
        defaultContent: DateInputProps = {

        }
        content = defaultContent | content
        component = self.create_component(
            'dateinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def RadioInput(self, 
            content: RadioInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[RadioInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A user input component that allows users to choose a single value from a list of options using radio buttons.
        """
        defaultContent: RadioInputProps = {
            "options": "{\n  \"a\": \"Option A\",\n  \"b\": \"Option B\"\n}",
            "orientation": "vertical",
        }
        content = defaultContent | content
        component = self.create_component(
            'radioinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def CheckboxInput(self, 
            content: CheckboxInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[CheckboxInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A user input component that allows users to choose multiple values from a list of options using checkboxes.
        """
        defaultContent: CheckboxInputProps = {
            "options": "{\n  \"a\": \"Option A\",\n  \"b\": \"Option B\"\n}",
            "orientation": "vertical",
        }
        content = defaultContent | content
        component = self.create_component(
            'checkboxinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def DropdownInput(self, 
            content: DropdownInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[DropdownInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A user input component that allows users to select a single value from a list of options using a dropdown menu.
        """
        defaultContent: DropdownInputProps = {
            "options": "{\n  \"a\": \"Option A\",\n  \"b\": \"Option B\"\n}",
        }
        content = defaultContent | content
        component = self.create_component(
            'dropdowninput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def SelectInput(self, 
            content: SelectInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[SelectInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A user input component that allows users to select a single value from a searchable list of options.
        """
        defaultContent: SelectInputProps = {
            "options": "{\n  \"a\": \"Option A\",\n  \"b\": \"Option B\"\n}",
            "maximumCount": "0",
            "chipTextColor": "#ffffff",
            "selectedColor": "rgba(210, 234, 244, 0.8)",
        }
        content = defaultContent | content
        component = self.create_component(
            'selectinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def MultiselectInput(self, 
            content: MultiselectInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[MultiselectInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A user input component that allows users to select multiple values from a searchable list of options.
        """
        defaultContent: MultiselectInputProps = {
            "options": "{\n  \"a\": \"Option A\",\n  \"b\": \"Option B\"\n}",
            "maximumCount": "0",
            "chipTextColor": "#ffffff",
            "selectedColor": "rgba(210, 234, 244, 0.8)",
        }
        content = defaultContent | content
        component = self.create_component(
            'multiselectinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def FileInput(self, 
            content: FileInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[FileInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A user input component that allows users to upload files.
        """
        defaultContent: FileInputProps = {
            "allowMultipleFiles": "no",
        }
        content = defaultContent | content
        component = self.create_component(
            'fileinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def WebcamCapture(self, 
            content: WebcamCaptureProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[WebcamCaptureEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A user input component that allows users to capture images using their webcam.
        """
        defaultContent: WebcamCaptureProps = {
            "refreshRate": "200",
        }
        content = defaultContent | content
        component = self.create_component(
            'webcamcapture',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def VegaLiteChart(self, 
            content: VegaLiteChartProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[VegaLiteChartEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A component that displays Vega-Lite/Altair charts.
        """
        defaultContent: VegaLiteChartProps = {
            "spec": "{\n  \"$schema\": \"https://vega.github.io/schema/vega-lite/v5.json\",\n  \"description\": \"A component that displays Vega-Lite/Altair charts.\",\n  \"data\": {\n    \"values\": [\n      {\n        \"a\": \"A\",\n        \"b\": 100\n      },\n      {\n        \"a\": \"B\",\n        \"b\": 200\n      },\n      {\n        \"a\": \"C\",\n        \"b\": 150\n      },\n      {\n        \"a\": \"D\",\n        \"b\": 300\n      }\n    ]\n  },\n  \"mark\": \"bar\",\n  \"encoding\": {\n    \"x\": {\n      \"field\": \"a\",\n      \"type\": \"nominal\"\n    },\n    \"y\": {\n      \"field\": \"b\",\n      \"type\": \"quantitative\"\n    }\n  }\n}",
        }
        content = defaultContent | content
        component = self.create_component(
            'vegalitechart',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def PlotlyGraph(self, 
            content: PlotlyGraphProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[PlotlyGraphEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A component that displays Plotly graphs.
        """
        defaultContent: PlotlyGraphProps = {
            "spec": "{\n  \"data\": [\n    {\n      \"x\": [\n        \"a\",\n        \"b\",\n        \"c\"\n      ],\n      \"y\": [\n        22,\n        25,\n        29\n      ],\n      \"type\": \"bar\"\n    }\n  ]\n}",
        }
        content = defaultContent | content
        component = self.create_component(
            'plotlygraph',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Metric(self, 
            content: MetricProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[MetricEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A component that prominently displays a metric value and associated information.
        """
        defaultContent: MetricProps = {
            "name": "Metric",
            "metricValue": "0",
            "positiveColor": "#00B800",
            "neutralColor": "var(--secondaryTextColor)",
            "negativeColor": "#FB0000",
        }
        content = defaultContent | content
        component = self.create_component(
            'metric',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Message(self, 
            content: MessageProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[MessageEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A component that displays a message in various styles, including success, error, warning, and informational.
        """
        defaultContent: MessageProps = {
            "successColor": "#00B800",
            "errorColor": "#FB0000",
            "warningColor": "#FB9600",
            "infoColor": "#00ADB8",
            "loadingColor": "#00ADB8",
        }
        content = defaultContent | content
        component = self.create_component(
            'message',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def VideoPlayer(self, 
            content: VideoPlayerProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[VideoPlayerEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A video player component that can play various video formats.
        """
        defaultContent: VideoPlayerProps = {
            "src": "",
            "controls": "yes",
            "autoplay": "no",
            "loop": "no",
            "muted": "no",
        }
        content = defaultContent | content
        component = self.create_component(
            'videoplayer',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Chat(self, 
            content: ChatProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[ChatEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A chat component to build human-to-AI interactions.
        """
        defaultContent: ChatProps = {
            "incomingInitials": "AI",
            "outgoingInitials": "YOU",
            "useMarkdown": "no",
            "enableFileUpload": "no",
            "placeholder": "Write something...",
            "outgoingColor": "#F5F5F9",
            "avatarBackgroundColor": "#2C2D30",
            "avatarTextColor": "#FFFFFF",
        }
        content = defaultContent | content
        component = self.create_component(
            'chat',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Step(self, 
            content: StepProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[StepEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A container component that displays its child components as a step inside a Step Container.
        """
        defaultContent: StepProps = {
            "name": "(No name)",
            "contentPadding": "16px",
            "isCompleted": "no",
            "contentHAlign": "unset",
        }
        content = defaultContent | content
        component = self.create_container_component(
            'step',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def StepContainer(self, 
            content: StepContainerProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[StepContainerEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A container component for displaying Step components, allowing you to implement a stepped workflow.
        """
        defaultContent: StepContainerProps = {

        }
        content = defaultContent | content
        component = self.create_container_component(
            'steps',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def RatingInput(self, 
            content: RatingInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[RatingInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A user input component that allows users to provide a rating.
        """
        defaultContent: RatingInputProps = {
            "feedback": "stars",
            "minValue": "1",
            "maxValue": "5",
            "valueStep": "1",
        }
        content = defaultContent | content
        component = self.create_component(
            'ratinginput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def Tags(self, 
            content: TagsProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[TagsEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A component to display coloured tag pills.
        """
        defaultContent: TagsProps = {
            "tags": "{}",
            "referenceColor": "#29cf00",
            "seed": "1",
            "rotateHue": "yes",
            "primaryTextColor": "#ffffff",
        }
        content = defaultContent | content
        component = self.create_component(
            'tags',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    def SwitchInput(self, 
            content: SwitchInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[SwitchInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            binding: Optional[Dict] = None,
            ) -> Component:
        """
        A user input component with a simple on/off status.
        """
        defaultContent: SwitchInputProps = {

        }
        content = defaultContent | content
        component = self.create_component(
            'switchinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
