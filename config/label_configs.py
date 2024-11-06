"""Label configurations"""

LABEL_CONFIGS = {
    "brush": """
    <View>
      <Image name="image" value="$image" zoom="true"/>
      <BrushLabels name="tag" toName="image">
        <Label value="drone" background="#002aff"/>
      </BrushLabels>
    </View>
    """,
    
    "rectangle": """
    <View>
      <Image name="image" value="$image" zoom="true"/>
      <RectangleLabels name="tag" toName="image">
        <Label value="drone" background="#002aff"/>
      </RectangleLabels>
    </View>
    """,
    
    "polygon": """
    <View>
      <Image name="image" value="$image" zoom="true"/>
      <PolygonLabels name="tag" toName="image">
        <Label value="drone" background="#002aff"/>
      </PolygonLabels>
    </View>
    """
}
