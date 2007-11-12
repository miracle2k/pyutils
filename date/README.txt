dateutil-parserinfo-override.diff 
*********************************

	This patch does apply to the python-dateutil package from:
		http://labix.org/lunatic-python. 
		
	The version retrieved at 12-nov-2007 (V1.2) has (what I would consider) a bug, by 
	not  allowing the use of:
		parse(parserinfo=MyParserInfo())
	with MyParserInfo being a descendant class. After applying this patch, you will be
	able to:
		* Pass both instances and classes (previously, passing an instance would cause
			an exception in issubclass()
		* Actually cause the custom class to take effect - previously, even it would
		    use still use the base "parserinfo" class, regardless of the parserinfo
		    parameter.
		* Both parser and parserinfo are now new-style classes to allow for better 
			inheritance support.