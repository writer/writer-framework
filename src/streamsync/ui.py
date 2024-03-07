from typing import TypedDict, Unpack
from typing import Optional
from streamsync.ui_manager import StreamsyncUI
from streamsync.core_ui import Component


class RootProps(TypedDict):
    appName: Optional[str]
    accentColor: Optional[str]
    primaryTextColor: Optional[str]
    secondaryTextColor: Optional[str]
    emptinessColor: Optional[str]
    containerBackgroundColor: Optional[str]
    containerShadow: Optional[str]
    separatorColor: Optional[str]
    buttonColor: Optional[str]
    buttonTextColor: Optional[str]
    buttonShadow: Optional[str]
    selectedColor: Optional[str]
    cssClasses: Optional[str]
    contentWidth: Optional[str]
    contentHAlign: Optional[str]
    contentVAlign: Optional[str]
    contentPadding: Optional[str]


class PageProps(TypedDict):
    key: Optional[str]
    pageMode: Optional[str]
    accentColor: Optional[str]
    primaryTextColor: Optional[str]
    secondaryTextColor: Optional[str]
    emptinessColor: Optional[str]
    containerBackgroundColor: Optional[str]
    containerShadow: Optional[str]
    separatorColor: Optional[str]
    buttonColor: Optional[str]
    buttonTextColor: Optional[str]
    buttonShadow: Optional[str]
    selectedColor: Optional[str]
    cssClasses: Optional[str]


class SidebarProps(TypedDict):
    startCollapsed: Optional[str]
    sidebarBackgroundColor: Optional[str]
    accentColor: Optional[str]
    primaryTextColor: Optional[str]
    secondaryTextColor: Optional[str]
    containerBackgroundColor: Optional[str]
    containerShadow: Optional[str]
    separatorColor: Optional[str]
    buttonColor: Optional[str]
    buttonTextColor: Optional[str]
    buttonShadow: Optional[str]
    cssClasses: Optional[str]


class ButtonProps(TypedDict):
    text: Optional[str]
    isDisabled: Optional[str]
    buttonColor: Optional[str]
    buttonTextColor: Optional[str]
    icon: Optional[str]
    buttonShadow: Optional[str]
    separatorColor: Optional[str]
    cssClasses: Optional[str]


class TextProps(TypedDict):
    text: Optional[str]
    useMarkdown: Optional[str]
    alignment: Optional[str]
    primaryTextColor: Optional[str]
    cssClasses: Optional[str]


class SectionProps(TypedDict):
    title: Optional[str]
    accentColor: Optional[str]
    primaryTextColor: Optional[str]
    secondaryTextColor: Optional[str]
    containerBackgroundColor: Optional[str]
    containerShadow: Optional[str]
    separatorColor: Optional[str]
    buttonColor: Optional[str]
    buttonTextColor: Optional[str]
    buttonShadow: Optional[str]
    contentPadding: Optional[str]
    contentHAlign: Optional[str]
    cssClasses: Optional[str]


class HeaderProps(TypedDict):
    text: Optional[str]
    accentColor: Optional[str]
    emptinessColor: Optional[str]
    cssClasses: Optional[str]


class HeadingProps(TypedDict):
    text: Optional[str]
    headingType: Optional[str]
    alignment: Optional[str]
    primaryTextColor: Optional[str]
    cssClasses: Optional[str]


class DataFrameProps(TypedDict):
    dataframe: Optional[str]
    showIndex: Optional[str]
    enableSearch: Optional[str]
    enableDownload: Optional[str]
    displayRowCount: Optional[str]
    wrapText: Optional[str]
    primaryTextColor: Optional[str]
    secondaryTextColor: Optional[str]
    separatorColor: Optional[str]
    dataframeBackgroundColor: Optional[str]
    dataframeHeaderRowBackgroundColor: Optional[str]
    fontStyle: Optional[str]
    cssClasses: Optional[str]


class HTMLElementProps(TypedDict):
    element: Optional[str]
    styles: Optional[str]
    attrs: Optional[str]
    htmlInside: Optional[str]
    cssClasses: Optional[str]


class PaginationProps(TypedDict):
    page: Optional[str]
    pageSize: Optional[str]
    totalItems: Optional[str]
    pageSizeOptions: Optional[str]
    pageSizeShowAll: Optional[str]
    jumpTo: Optional[str]


class RepeaterProps(TypedDict):
    repeaterObject: Optional[str]
    keyVariable: Optional[str]
    valueVariable: Optional[str]


class ColumnProps(TypedDict):
    title: Optional[str]
    width: Optional[str]
    isSticky: Optional[str]
    isCollapsible: Optional[str]
    startCollapsed: Optional[str]
    separatorColor: Optional[str]
    contentPadding: Optional[str]
    contentHAlign: Optional[str]
    contentVAlign: Optional[str]
    cssClasses: Optional[str]


class ColumnContainerProps(TypedDict):
    cssClasses: Optional[str]


class TabProps(TypedDict):
    name: Optional[str]
    contentPadding: Optional[str]
    contentHAlign: Optional[str]
    cssClasses: Optional[str]


class TabContainerProps(TypedDict):
    accentColor: Optional[str]
    primaryTextColor: Optional[str]
    secondaryTextColor: Optional[str]
    containerBackgroundColor: Optional[str]
    containerShadow: Optional[str]
    separatorColor: Optional[str]
    buttonColor: Optional[str]
    buttonTextColor: Optional[str]
    buttonShadow: Optional[str]
    cssClasses: Optional[str]


class LinkProps(TypedDict):
    url: Optional[str]
    target: Optional[str]
    rel: Optional[str]
    text: Optional[str]
    primaryTextColor: Optional[str]
    cssClasses: Optional[str]


class HorizontalStackProps(TypedDict):
    contentPadding: Optional[str]
    contentHAlign: Optional[str]
    cssClasses: Optional[str]


class SeparatorProps(TypedDict):
    separatorColor: Optional[str]
    cssClasses: Optional[str]


class ImageProps(TypedDict):
    src: Optional[str]
    caption: Optional[str]
    maxWidth: Optional[str]
    maxHeight: Optional[str]
    secondaryTextColor: Optional[str]
    cssClasses: Optional[str]


class PDFProps(TypedDict):
    source: Optional[str]
    highlights: Optional[str]
    selectedMatch: Optional[str]
    page: Optional[str]
    controls: Optional[str]
    containerBackgroundColor: Optional[str]
    separatorColor: Optional[str]
    primaryTextColor: Optional[str]
    cssClasses: Optional[str]


class IFrameProps(TypedDict):
    src: Optional[str]
    cssClasses: Optional[str]


class GoogleMapsProps(TypedDict):
    apiKey: Optional[str]
    mapId: Optional[str]
    mapType: Optional[str]
    zoom: Optional[str]
    lat: Optional[str]
    lng: Optional[str]
    markers: Optional[str]
    cssClasses: Optional[str]


class MapboxProps(TypedDict):
    accessToken: Optional[str]
    mapStyle: Optional[str]
    zoom: Optional[str]
    lat: Optional[str]
    lng: Optional[str]
    markers: Optional[str]
    controls: Optional[str]
    cssClasses: Optional[str]


class IconProps(TypedDict):
    icon: Optional[str]
    size: Optional[str]
    color: Optional[str]
    cssClasses: Optional[str]


class TimerProps(TypedDict):
    intervalMs: Optional[str]
    isActive: Optional[str]
    accentColor: Optional[str]
    cssClasses: Optional[str]


class TextInputProps(TypedDict):
    label: Optional[str]
    placeholder: Optional[str]
    passwordMode: Optional[str]
    cssClasses: Optional[str]


class TextareaInputProps(TypedDict):
    label: Optional[str]
    placeholder: Optional[str]
    rows: Optional[str]
    cssClasses: Optional[str]


class NumberInputProps(TypedDict):
    label: Optional[str]
    placeholder: Optional[str]
    minValue: Optional[str]
    maxValue: Optional[str]
    valueStep: Optional[str]
    cssClasses: Optional[str]


class SliderInputProps(TypedDict):
    label: Optional[str]
    minValue: Optional[str]
    maxValue: Optional[str]
    stepSize: Optional[str]
    cssClasses: Optional[str]


class DateInputProps(TypedDict):
    label: Optional[str]
    cssClasses: Optional[str]


class RadioInputProps(TypedDict):
    label: Optional[str]
    options: Optional[str]
    orientation: Optional[str]
    cssClasses: Optional[str]


class CheckboxInputProps(TypedDict):
    label: Optional[str]
    options: Optional[str]
    orientation: Optional[str]
    cssClasses: Optional[str]


class DropdownInputProps(TypedDict):
    label: Optional[str]
    options: Optional[str]
    cssClasses: Optional[str]


class SelectInputProps(TypedDict):
    label: Optional[str]
    options: Optional[str]
    placeholder: Optional[str]
    maximumCount: Optional[str]
    accentColor: Optional[str]
    chipTextColor: Optional[str]
    selectedColor: Optional[str]
    primaryTextColor: Optional[str]
    secondaryTextColor: Optional[str]
    containerBackgroundColor: Optional[str]
    separatorColor: Optional[str]
    cssClasses: Optional[str]


class MultiselectInputProps(TypedDict):
    label: Optional[str]
    options: Optional[str]
    placeholder: Optional[str]
    maximumCount: Optional[str]
    accentColor: Optional[str]
    chipTextColor: Optional[str]
    selectedColor: Optional[str]
    primaryTextColor: Optional[str]
    secondaryTextColor: Optional[str]
    containerBackgroundColor: Optional[str]
    separatorColor: Optional[str]
    cssClasses: Optional[str]


class FileInputProps(TypedDict):
    label: Optional[str]
    allowMultipleFiles: Optional[str]
    cssClasses: Optional[str]


class WebcamCaptureProps(TypedDict):
    refreshRate: Optional[str]
    buttonColor: Optional[str]
    buttonTextColor: Optional[str]
    buttonShadow: Optional[str]
    separatorColor: Optional[str]
    cssClasses: Optional[str]


class VegaLiteChartProps(TypedDict):
    spec: Optional[str]
    cssClasses: Optional[str]


class PlotlyGraphProps(TypedDict):
    spec: Optional[str]
    cssClasses: Optional[str]


class MetricProps(TypedDict):
    name: Optional[str]
    metricValue: Optional[str]
    description: Optional[str]
    note: Optional[str]
    primaryTextColor: Optional[str]
    secondaryTextColor: Optional[str]
    positiveColor: Optional[str]
    neutralColor: Optional[str]
    negativeColor: Optional[str]
    cssClasses: Optional[str]


class MessageProps(TypedDict):
    message: Optional[str]
    successColor: Optional[str]
    errorColor: Optional[str]
    warningColor: Optional[str]
    infoColor: Optional[str]
    loadingColor: Optional[str]
    primaryTextColor: Optional[str]
    cssClasses: Optional[str]


class VideoPlayerProps(TypedDict):
    src: Optional[str]
    controls: Optional[str]
    autoplay: Optional[str]
    loop: Optional[str]
    muted: Optional[str]
    cssClasses: Optional[str]


class ChatProps(TypedDict):
    incomingInitials: Optional[str]
    outgoingInitials: Optional[str]
    useMarkdown: Optional[str]
    incomingColor: Optional[str]
    outgoingColor: Optional[str]
    avatarBackgroundColor: Optional[str]
    avatarTextColor: Optional[str]
    containerBackgroundColor: Optional[str]
    primaryTextColor: Optional[str]
    secondaryTextColor: Optional[str]
    separatorColor: Optional[str]
    buttonColor: Optional[str]
    buttonTextColor: Optional[str]
    cssClasses: Optional[str]


class StepProps(TypedDict):
    name: Optional[str]
    contentPadding: Optional[str]
    isCompleted: Optional[str]
    contentHAlign: Optional[str]
    cssClasses: Optional[str]


class StepContainerProps(TypedDict):
    accentColor: Optional[str]
    primaryTextColor: Optional[str]
    secondaryTextColor: Optional[str]
    containerBackgroundColor: Optional[str]
    containerShadow: Optional[str]
    separatorColor: Optional[str]
    buttonColor: Optional[str]
    buttonTextColor: Optional[str]
    buttonShadow: Optional[str]
    cssClasses: Optional[str]


class RatingInputProps(TypedDict):
    label: Optional[str]
    feedback: Optional[str]
    minValue: Optional[str]
    maxValue: Optional[str]
    valueStep: Optional[str]
    accentColor: Optional[str]
    primaryTextColor: Optional[str]
    cssClasses: Optional[str]


class StreamsyncUIManager(StreamsyncUI):
    """The StreamsyncUIManager class is intended to include dynamically-
    generated methods corresponding to UI components defined in the Vue
    frontend during the build process.

    This class serves as a bridge for programmatically interacting with the
    frontend, allowing methods to adapt to changes in the UI components without
    manual updates.
    """

    def Root(self, **kwargs: Unpack[RootProps]) -> Component:
        """
        The root component of the application, which serves as the starting point of the component hierarchy.
        """
        component_context = self.create_container_component('root', **kwargs)
        return component_context

    def Page(self, **kwargs: Unpack[PageProps]) -> Component:
        """
        A container component representing a single page within the application.
        """
        component_context = self.create_container_component('page', **kwargs)
        return component_context

    def Sidebar(self, **kwargs: Unpack[SidebarProps]) -> Component:
        """
        A container component that organises its children in a sidebar. Its parent must be a Page component.
        """
        component_context = self.create_container_component('sidebar', **kwargs)
        return component_context

    def Button(self, **kwargs: Unpack[ButtonProps]) -> Component:
        """
        A standalone button component that can be linked to a click event handler.
        """
        component_context = self.create_component('button', **kwargs)
        return component_context

    def Text(self, **kwargs: Unpack[TextProps]) -> Component:
        """
        A component to display plain text or formatted text using Markdown syntax.
        """
        component_context = self.create_component('text', **kwargs)
        return component_context

    def Section(self, **kwargs: Unpack[SectionProps]) -> Component:
        """
        A container component that divides the layout into sections, with an optional title.
        """
        component_context = self.create_container_component('section', **kwargs)
        return component_context

    def Header(self, **kwargs: Unpack[HeaderProps]) -> Component:
        """
        A container component that typically contains the main navigation elements.
        """
        component_context = self.create_container_component('header', **kwargs)
        return component_context

    def Heading(self, **kwargs: Unpack[HeadingProps]) -> Component:
        """
        A text component used to display headings or titles in different sizes and styles.
        """
        component_context = self.create_component('heading', **kwargs)
        return component_context

    def DataFrame(self, **kwargs: Unpack[DataFrameProps]) -> Component:
        """
        A component to display Pandas DataFrames.
        """
        component_context = self.create_component('dataframe', **kwargs)
        return component_context

    def HTMLElement(self, **kwargs: Unpack[HTMLElementProps]) -> Component:
        """
        A generic component that creates customisable HTML elements, which can serve as containers for other components.
        """
        component_context = self.create_container_component('htmlelement', **kwargs)
        return component_context

    def Pagination(self, **kwargs: Unpack[PaginationProps]) -> Component:
        """
        A component that can help you paginate records, for example from a Repeater or a DataFrame.
        """
        component_context = self.create_component('pagination', **kwargs)
        return component_context

    def Repeater(self, **kwargs: Unpack[RepeaterProps]) -> Component:
        """
        A container component that repeats its child components based on a dictionary.
        """
        component_context = self.create_container_component('repeater', **kwargs)
        return component_context

    def Column(self, **kwargs: Unpack[ColumnProps]) -> Component:
        """
        A layout component that organises its child components in columns. Must be inside a Column Container component.
        """
        component_context = self.create_container_component('column', **kwargs)
        return component_context

    def ColumnContainer(self, **kwargs: Unpack[ColumnContainerProps]) -> Component:
        """
        Serves as container for Column components
        """
        component_context = self.create_container_component('columns', **kwargs)
        return component_context

    def Tab(self, **kwargs: Unpack[TabProps]) -> Component:
        """
        A container component that displays its child components as a tab inside a Tab Container.
        """
        component_context = self.create_container_component('tab', **kwargs)
        return component_context

    def TabContainer(self, **kwargs: Unpack[TabContainerProps]) -> Component:
        """
        A container component for organising and displaying Tab components in a tabbed interface.
        """
        component_context = self.create_container_component('tabs', **kwargs)
        return component_context

    def Link(self, **kwargs: Unpack[LinkProps]) -> Component:
        """
        A component to create a hyperlink.
        """
        component_context = self.create_component('link', **kwargs)
        return component_context

    def HorizontalStack(self, **kwargs: Unpack[HorizontalStackProps]) -> Component:
        """
        A layout component that stacks its child components horizontally, wrapping them to the next row if necessary.
        """
        component_context = self.create_container_component('horizontalstack', **kwargs)
        return component_context

    def Separator(self, **kwargs: Unpack[SeparatorProps]) -> Component:
        """
        A visual component to create a separation between adjacent elements.
        """
        component_context = self.create_component('separator', **kwargs)
        return component_context

    def Image(self, **kwargs: Unpack[ImageProps]) -> Component:
        """
        A component to display images.
        """
        component_context = self.create_component('image', **kwargs)
        return component_context

    def PDF(self, **kwargs: Unpack[PDFProps]) -> Component:
        """
        A component to embed PDF documents.
        """
        component_context = self.create_component('pdf', **kwargs)
        return component_context

    def IFrame(self, **kwargs: Unpack[IFrameProps]) -> Component:
        """
        A component to embed an external resource in an iframe.
        """
        component_context = self.create_component('iframe', **kwargs)
        return component_context

    def GoogleMaps(self, **kwargs: Unpack[GoogleMapsProps]) -> Component:
        """
        A component to embed a Google Map. It can be used to display a map with markers.
        """
        component_context = self.create_component('googlemaps', **kwargs)
        return component_context

    def Mapbox(self, **kwargs: Unpack[MapboxProps]) -> Component:
        """
        A component to embed a Mapbox map. It can be used to display a map with markers.
        """
        component_context = self.create_component('mapbox', **kwargs)
        return component_context

    def Icon(self, **kwargs: Unpack[IconProps]) -> Component:
        """
        A component to display an icon
        """
        component_context = self.create_component('icon', **kwargs)
        return component_context

    def Timer(self, **kwargs: Unpack[TimerProps]) -> Component:
        """
        A component that emits an event repeatedly at specified time intervals, enabling time-based refresh.
        """
        component_context = self.create_component('timer', **kwargs)
        return component_context

    def TextInput(self, **kwargs: Unpack[TextInputProps]) -> Component:
        """
        A user input component that allows users to enter single-line text values.
        """
        component_context = self.create_component('textinput', **kwargs)
        return component_context

    def TextareaInput(self, **kwargs: Unpack[TextareaInputProps]) -> Component:
        """
        A user input component that allows users to enter multi-line text values.
        """
        component_context = self.create_component('textareainput', **kwargs)
        return component_context

    def NumberInput(self, **kwargs: Unpack[NumberInputProps]) -> Component:
        """
        A user input component that allows users to enter numeric values.
        """
        component_context = self.create_component('numberinput', **kwargs)
        return component_context

    def SliderInput(self, **kwargs: Unpack[SliderInputProps]) -> Component:
        """
        A user input component that allows users to select numeric values using a slider with optional constraints like min, max, and step.
        """
        component_context = self.create_component('sliderinput', **kwargs)
        return component_context

    def DateInput(self, **kwargs: Unpack[DateInputProps]) -> Component:
        """
        A user input component that allows users to select a date using a date picker interface.
        """
        component_context = self.create_component('dateinput', **kwargs)
        return component_context

    def RadioInput(self, **kwargs: Unpack[RadioInputProps]) -> Component:
        """
        A user input component that allows users to choose a single value from a list of options using radio buttons.
        """
        component_context = self.create_component('radioinput', **kwargs)
        return component_context

    def CheckboxInput(self, **kwargs: Unpack[CheckboxInputProps]) -> Component:
        """
        A user input component that allows users to choose multiple values from a list of options using checkboxes.
        """
        component_context = self.create_component('checkboxinput', **kwargs)
        return component_context

    def DropdownInput(self, **kwargs: Unpack[DropdownInputProps]) -> Component:
        """
        A user input component that allows users to select a single value from a list of options using a dropdown menu.
        """
        component_context = self.create_component('dropdowninput', **kwargs)
        return component_context

    def SelectInput(self, **kwargs: Unpack[SelectInputProps]) -> Component:
        """
        A user input component that allows users to select a single value from a searchable list of options.
        """
        component_context = self.create_component('selectinput', **kwargs)
        return component_context

    def MultiselectInput(self, **kwargs: Unpack[MultiselectInputProps]) -> Component:
        """
        A user input component that allows users to select multiple values from a searchable list of options.
        """
        component_context = self.create_component('multiselectinput', **kwargs)
        return component_context

    def FileInput(self, **kwargs: Unpack[FileInputProps]) -> Component:
        """
        A user input component that allows users to upload files.
        """
        component_context = self.create_component('fileinput', **kwargs)
        return component_context

    def WebcamCapture(self, **kwargs: Unpack[WebcamCaptureProps]) -> Component:
        """
        A user input component that allows users to capture images using their webcam.
        """
        component_context = self.create_component('webcamcapture', **kwargs)
        return component_context

    def VegaLiteChart(self, **kwargs: Unpack[VegaLiteChartProps]) -> Component:
        """
        A component that displays Vega-Lite/Altair charts.
        """
        component_context = self.create_component('vegalitechart', **kwargs)
        return component_context

    def PlotlyGraph(self, **kwargs: Unpack[PlotlyGraphProps]) -> Component:
        """
        A component that displays Plotly graphs.
        """
        component_context = self.create_component('plotlygraph', **kwargs)
        return component_context

    def Metric(self, **kwargs: Unpack[MetricProps]) -> Component:
        """
        A component that prominently displays a metric value and associated information.
        """
        component_context = self.create_component('metric', **kwargs)
        return component_context

    def Message(self, **kwargs: Unpack[MessageProps]) -> Component:
        """
        A component that displays a message in various styles, including success, error, warning, and informational.
        """
        component_context = self.create_component('message', **kwargs)
        return component_context

    def VideoPlayer(self, **kwargs: Unpack[VideoPlayerProps]) -> Component:
        """
        A video player component that can play various video formats.
        """
        component_context = self.create_component('videoplayer', **kwargs)
        return component_context

    def Chat(self, **kwargs: Unpack[ChatProps]) -> Component:
        """
        A chat component to build human-to-AI interactions.
        """
        component_context = self.create_component('chat', **kwargs)
        return component_context

    def Step(self, **kwargs: Unpack[StepProps]) -> Component:
        """
        A container component that displays its child components as a step inside a Step Container.
        """
        component_context = self.create_container_component('step', **kwargs)
        return component_context

    def StepContainer(self, **kwargs: Unpack[StepContainerProps]) -> Component:
        """
        A container component for displaying Step components, allowing you to implement a stepped workflow.
        """
        component_context = self.create_container_component('steps', **kwargs)
        return component_context

    def RatingInput(self, **kwargs: Unpack[RatingInputProps]) -> Component:
        """
        A user input component that allows users to provide a rating.
        """
        component_context = self.create_component('ratinginput', **kwargs)
        return component_context
